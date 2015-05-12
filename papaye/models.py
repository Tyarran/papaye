import collections
import copy
import datetime
import hashlib
import io
import itertools
import json
import logging
import magic
import pkg_resources
import requests

from BTrees.OOBTree import OOBTree
from ZODB.blob import Blob
from beaker.cache import cache_region
from persistent import Persistent
from pkg_resources import parse_version
from pyramid.security import Allow, ALL_PERMISSIONS, Everyone
from pyramid.threadlocal import get_current_registry
from pyramid_zodbconn import db_from_uri
from pytz import utc
from repoze.evolution import ZODBEvolutionManager
from requests.exceptions import ConnectionError

from papaye.factories import user_root_factory, repository_root_factory, APP_ROOT_NAME
from papaye.schemas import Metadata


logger = logging.getLogger(__name__)
status_type = collections.namedtuple('status', ('local', 'cached', 'distant'))
SW_VERSION = 5
STATUS = status_type(*range(0, len(status_type._fields)))


def get_manager(config):
    conn = config.registry._zodb_databases[''].open()
    root = conn.root()[APP_ROOT_NAME]
    manager = ZODBEvolutionManager(
        root,
        evolve_packagename='papaye.evolve',
        sw_version=SW_VERSION,
        initial_db_version=0
    )
    return manager


def format_key(key):
    return pkg_resources.safe_name(key.lower())


def get_connection(settings):
    uri = settings.get('zodbconn.uri', None)
    db = db_from_uri(uri, 'unamed', None)
    return db.open()


def chunk(iterable, step):
    for i in range(0, len(iterable), step):
        yield iterable[i:i+step]


class MyOOBTree(OOBTree):

    def _p_resolveConflict(self, old_state, stored_state, new_state):
        merged_state = {}
        if old_state is None:
            old_state = (((tuple(), ), ), )
        pr_name_old = list(itertools.islice(old_state[0][0], 0, None, 2)) if old_state is not None else []
        try:
            for pr in stored_state[0][0]:
                if pr[0] not in pr_name_old:
                    merged_state.update(dict(chunk(pr, 2)))

            for pr in new_state[0][0]:
                if pr[0] not in pr_name_old:
                    merged_state.update(dict(chunk(pr, 2)))
            new_old_state = ((((tuple(itertools.chain(*list(merged_state.items())))), ), ), )  # OOBtree state. Beurk!
            return super()._p_resolveConflict(new_old_state, stored_state, new_state)
        except:
            return old_state


class BaseModel(Persistent):
    __name__ = ''

    def __repr__(self):
        return '<{}.{} "{}" at {}>'.format(self.__module__, self.__class__.__name__, self.__name__, id(self))

    @classmethod
    def clone(cls, model_obj):
        """Return a clone on given object"""
        clone = cls.__new__(cls)
        for key, value in model_obj.__dict__.items():
            if isinstance(value, Blob):
                setattr(clone, key, Blob(value.open().read()))
            else:
                setattr(clone, key, copy.copy(value))
        clone.__name__ = model_obj.__name__
        return clone


class SubscriptableBaseModel(BaseModel):
    subobjects_attr = None

    def get_subobjects(self):
        return getattr(self, self.subobjects_attr)

    def get(self, key, default=None):
        getitem_object = self.get_subobjects()
        if key in getitem_object.keys():
            return getitem_object[key]
        else:
            return default

    def __contains__(self, obj_or_name):
        if isinstance(obj_or_name, str):
            elements = list(self.get_subobjects())
        else:
            subobjects = self.get_subobjects()
            elements = [subobjects[element] for element in subobjects]
        return obj_or_name in elements

    def __iter__(self):
        return (self.get_subobjects()[item] for item in self.get_subobjects())

    def __len__(self):
        return len(list(getattr(self, self.subobjects_attr)))

    def __delitem__(self, key):
        key = format_key(key)
        del(self.get_subobjects()[key])

    def keys(self):
        return (elem for elem in self.get_subobjects())


class Root(SubscriptableBaseModel):
    __name__ = __parent__ = None
    subobjects_attr = 'packages'

    def __init__(self):
        self.packages = MyOOBTree()

    def __acl__(self):
        acl = [
            (Allow, 'group:installer', 'install'),
            (Allow, 'group:admin', ALL_PERMISSIONS)
        ]
        registry = get_current_registry()
        anonymous_install = registry.settings.get('papaye.anonymous_install')
        anonymous_install = True if anonymous_install and anonymous_install == 'true' else False
        if anonymous_install:
            acl.append((Allow, Everyone, 'install'))
        return acl

    def __iter__(self):
        return (package for package in self.get_subobjects().values())

    def __getitem__(self, name_or_index):
        if isinstance(name_or_index, int):
            return next(itertools.islice(self.__iter__(), name_or_index, name_or_index + 1))
        keys = [key for key in self.get_subobjects().keys()
                if format_key(key) == format_key(name_or_index)]
        if len(keys) == 1:
            return self.get_subobjects()[keys[0]]

    def __setitem__(self, key, package):
        if not hasattr(self, '_p_updated_keys'):
            self._p_updated_keys = []
        self._p_updated_keys.append(key)
        if isinstance(package, Package):
            package.__parent__ = self
        self.get_subobjects()[key] = package


class Package(SubscriptableBaseModel):
    pypi_url = 'http://pypi.python.org/pypi/{}/json'
    subobjects_attr = 'releases'

    def __init__(self, name):
        self.__name__ = name
        self.name = name
        self.releases = MyOOBTree()

    def __getitem__(self, release_name_or_index):
        if isinstance(release_name_or_index, int):
            return next(itertools.islice(self.__iter__(), release_name_or_index, release_name_or_index + 1))
        return self.releases[release_name_or_index]

    def __setitem__(self, key, value):
        key = format_key(key)
        self.releases[key] = value
        self.releases[key].__parent__ = self

    @classmethod
    @cache_region('pypi', 'get_last_remote_filename')
    def get_last_remote_version(cls, proxy, package_name):
        logger.debug('Not in cache')
        if not proxy:
            return None
        try:
            result = requests.get('http://pypi.python.org/pypi/{}/json'.format(package_name))
            if not result.status_code == 200:
                return None
            result = json.loads(result.content.decode('utf-8'))
            return result['info']['version']
        except ConnectionError:
            pass
        return None

    def repository_is_up_to_date(self, last_remote_release):
        if not last_remote_release:
            return True
        remote_version = parse_version(last_remote_release)

        local_versions = [release.version for release in self.releases.values()]
        for version in local_versions:
            if parse_version(version) >= remote_version:
                return True
        return False

    @classmethod
    def by_name(cls, name, request):
        if hasattr(request, 'root') and request.root is not None:
            root = request.root
        else:
            root = repository_root_factory(request)
        return root[name] if name in [package.__name__ for package in root] else None

    def get_last_release(self):
        if not len(self):
            return None
        elif len(self) == 1:
            return list(self)[0]
        max_version = max([parse_version(version) for version in self.releases.keys()])
        for version, release in self.releases.items():
            if parse_version(version) == max_version:
                return release

    @property
    def metadata(self):
        last_release = self.get_last_release()
        if last_release is not None:
            return last_release.metadata
        else:
            return {}


class Release(SubscriptableBaseModel):
    subobjects_attr = 'release_files'

    def __init__(self, name, version, metadata, deserialize_metadata=True):
        self.__name__ = name
        self.release_files = MyOOBTree()
        self.version = version
        self.original_metadata = metadata
        if deserialize_metadata:
            schema = Metadata()
            self.metadata = schema.serialize(metadata)
            self.metadata = schema.deserialize(self.metadata)

    def __getitem__(self, name_or_index):
        if isinstance(name_or_index, int):
            return next(itertools.islice(self.__iter__(), name_or_index, name_or_index + 1))
        return self.release_files[format_key(name_or_index)]

    def __setitem__(self, key, value):
        key = format_key(key)
        self.release_files[key] = value
        self.release_files[key].__parent__ = self

    @classmethod
    def by_packagename(cls, package_name, request):
        root = repository_root_factory(request)
        if package_name not in [pkg.__name__ for pkg in root]:
            return None
        return list(root[package_name].releases.values())

    @classmethod
    def by_releasename(cls, package_name, release, request):
        if hasattr(request, 'root') and request.root is not None:
            root = request.root
        else:
            root = repository_root_factory(request)
        if package_name in [pkg.__name__ for pkg in root]:
            return root[package_name].get(release, None)


class ReleaseFile(BaseModel):

    def __init__(self, filename, content, md5_digest=None, status=None):
        self.filename = self.__name__ = filename
        self.md5_digest = md5_digest
        self.set_content(content)
        self.upload_date = datetime.datetime.now(tz=utc)
        self.status = status if status is not None else STATUS.cached

    def get_content_type(self, content):
        buf = io.BytesIO(content)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            self.content_type = m.id_buffer(buf.read())

    def set_content(self, content):
        self.content = Blob(content)
        self.content_type = self.get_content_type(content)
        self.size = len(content)

    @classmethod
    def clone(cls, model_obj):
        """Return a clone on given object"""
        clone = cls.__new__(cls)
        clone.__name__ = model_obj.__name__
        clone.filename = model_obj.filename
        clone.md5_digest = model_obj.md5_digest
        clone.size = model_obj.size
        setattr(clone, 'content', Blob(model_obj.content.open().read()))
        clone.upload_date = copy.copy(model_obj.upload_date)
        clone.content_type = model_obj.content_type
        clone.status = model_obj.status
        return clone

    @classmethod
    def by_releasefilename(cls, package, release, releasefile, request):
        if hasattr(request, 'root') and request.root is not None:
            root = request.root
        else:
            root = repository_root_factory(request)
        if package in [pkg.__name__ for pkg in root] and root[package].get(release):
            return root[package][release].get(releasefile, None)


class User(BaseModel):

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = self.hash_password(password)
        self.groups = kwargs.get('groups', [])

    def hash_password(self, password):
        return hashlib.sha512(password.encode('utf-8')).hexdigest()

    def password_verify(self, clear_password):
        return self.hash_password(clear_password) == self.password

    def __repr__(self):
        return '<{}.{} "{}" at {}>'.format(self.__module__, self.__class__.__name__, self.username, id(self))

    @classmethod
    def by_username(cls, username, request):
        """Return user instance by username"""
        root = user_root_factory(request)
        if username in [user.username for user in root]:
            return root[username]
        return None


class RestrictedContext(object):

    def __acl__(self):
        # from pyramid.security import Everyone
        return [
            (Allow, 'test', ALL_PERMISSIONS)
            # (Allow, Everyone, ALL_PERMISSIONS)
        ]

    def __init__(self):
        pass
