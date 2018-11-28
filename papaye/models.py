import copy
import collections
import datetime
import hashlib
import io
import itertools
import json
import logging
import magic
import os
import pkg_resources
import requests
import uuid

from BTrees.OOBTree import OOBTree
from beaker.cache import cache_region
from persistent import Persistent
from pkg_resources import parse_version
from pyramid.config import ConfigurationError
from pyramid.interfaces import ISettings
from pyramid.security import Allow, Everyone, Authenticated
from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import get_current_request
from pyramid_zodbconn import db_from_uri
from pytz import utc
from requests.exceptions import ConnectionError
from zope.component import getGlobalSiteManager

from papaye.evolve.managers import PapayeEvolutionManager
from papaye.factories.root import user_root_factory, repository_root_factory
from papaye.schemas import Metadata
from papaye.serializers import ReleaseAPISerializer, PackageListSerializer


logger = logging.getLogger(__name__)
status_type = collections.namedtuple("status", ("local", "cached", "distant"))
SW_VERSION = 8
STATUS = status_type(*range(0, len(status_type._fields)))


def get_manager(config):
    manager = PapayeEvolutionManager(
        config,
        evolve_packagename="papaye.evolve",
        sw_version=SW_VERSION,
        initial_db_version=0,
    )
    return manager


# def format_key(key):
#     safe_name = pkg_resources.safe_name(key.lower())
#     return safe_name.replace('.', '-')


def get_connection(settings):
    uri = settings.get("zodbconn.uri", None)
    db = db_from_uri(uri, "unamed", None)
    return db.open()


def chunk(iterable, step):
    for i in range(0, len(iterable), step):
        yield iterable[i : i + step]


class MyOOBTree(OOBTree):
    def _p_resolveConflict(self, old_state, stored_state, new_state):
        merged_state = {}
        if old_state is None:
            old_state = (((tuple(),),),)
        pr_name_old = (
            list(itertools.islice(old_state[0][0], 0, None, 2))
            if old_state is not None
            else []
        )
        try:
            for pr in stored_state[0][0]:
                if pr[0] not in pr_name_old:
                    merged_state.update(dict(chunk(pr, 2)))

            for pr in new_state[0][0]:
                new_old_state = (
                    (((tuple(itertools.chain(*list(merged_state.items())))),),),
                )  # OOBtree state. Beurk!
                return super()._p_resolveConflict(
                    new_old_state, stored_state, new_state
                )
        except:
            return old_state


class Model(Persistent):
    def __repr__(self):
        return '<{}.{} "{}" at {}>'.format(
            self.__module__, self.__class__.__name__, self.__name__, id(self)
        )

    def __init__(self, *args, **kwargs):
        # Breaks the super() calls chain
        pass

    def __getattr__(self, attribute):
        # Breaks the super() calls chain
        return self.__getattribute__(attribute)


class ClonableModelMixin(object):
    @classmethod
    def clone(cls, model_obj):
        """Return a clone on given object"""
        clone = cls.__new__(cls)
        for key, value in model_obj.__dict__.items():
            setattr(clone, key, copy.copy(value))
        return clone


class SubscriptableMixin(object):
    _subobjects_attr = None
    _parent_name = None
    _name_attribute = "name"

    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.name = name
        if kwargs.get(self._parent_name) is not None:
            self.__parent__[self.format_key(self.__name__)] = self

    @property
    def __name__(self):
        return getattr(self, self._name_attribute, None)

    @property
    def __parent__(self):
        return getattr(self, self._parent_name, None)

    @property
    def subobjects(self):
        return getattr(self, self._subobjects_attr)

    def get(self, key, default=None):
        getitem_object = self.subobjects
        if key in getitem_object.keys():
            return getitem_object[key]
        else:
            return default

    def child(self, subobject):
        key = self.format_key(subobject.__name__)
        self._subobjects[key] = subobject
        self._subobjects[key].__parent__ = self
        return self

    def __contains__(self, obj_or_name):
        if isinstance(obj_or_name, str):
            elements = list(self.subobjects)
        else:
            elements = [
                self._subobjects[element] for element in self.subobjects
            ]
        return obj_or_name in elements

    def __iter__(self):
        return (self.subobjects[item] for item in self.subobjects)

    def __len__(self):
        return len(list(getattr(self, self._subobjects_attr)))

    def __delitem__(self, key):
        key = self.format_key(key)
        del (self.subobjects[key])

    def keys(self):
        return (elem for elem in self.subobjects)

    def format_key(self, key):
        return pkg_resources.safe_name(key.lower())


SubscriptableBaseModel = SubscriptableMixin


class Root(ClonableModelMixin, SubscriptableBaseModel, Model):
    _subobjects_attr = "packages"
    __name__ = ""

    def __init__(self, name):
        self.name = name
        self.packages = MyOOBTree()

    @property
    def __parent__(self):
        """Root object has no parent"""
        return None

    def __acl__(self):
        acl = [
            # (Allow, 'group:installer', 'install'),
            # (Allow, 'group:admin', ALL_PERMISSIONS)
            (Allow, Authenticated, "view")
        ]
        registry = get_current_registry()
        anonymous_install = registry.settings.get("papaye.anonymous_install")
        acl.append(
            (Allow, Everyone, "install")
        ) if anonymous_install and anonymous_install == "true" else False
        return acl

    def __iter__(self):
        return (package for package in self.subobjects.values())

    def __getitem__(self, name_or_index):
        if isinstance(name_or_index, int):
            return next(
                itertools.islice(
                    self.__iter__(), name_or_index, name_or_index + 1
                )
            )
        keys = [
            key
            for key in self.subobjects.keys()
            if self.format_key(key) == self.format_key(name_or_index)
        ]
        if len(keys) == 1:
            return self.subobjects[keys[0]]

    def __setitem__(self, key, package):
        if not hasattr(self, "_p_updated_keys"):
            self._p_updated_keys = []
        self._p_updated_keys.append(key)
        self.subobjects[key] = package


class Package(SubscriptableMixin, ClonableModelMixin, Model):
    pypi_url = "http://pypi.python.org/pypi/{}/json"
    _subobjects_attr = "releases"
    _name_atribute = "name"
    _parent_name = "root"

    def __init__(self, name, root=None, **kwargs):
        self.name = name
        self.releases = MyOOBTree()
        self.root = root
        super().__init__(name, root=root, **kwargs)

    def format_key(self, key):
        safe_name = pkg_resources.safe_name(key.lower())
        return safe_name.replace(".", "-")

    def __getitem__(self, release_name_or_index):
        try:
            if isinstance(release_name_or_index, int):
                return next(
                    itertools.islice(
                        self.__iter__(),
                        release_name_or_index,
                        release_name_or_index + 1,
                    )
                )
            return self.releases[release_name_or_index]
        except (KeyError, IndexError, StopIteration):
            return None

    def __setitem__(self, key, value):
        self.releases[key] = value

    @classmethod
    @cache_region("pypi", "get_last_remote_filename")
    def get_last_remote_version(cls, proxy, package_name):
        logger.debug("Not in cache")
        if not proxy:
            return None
        try:
            result = requests.get(
                "http://pypi.python.org/pypi/{}/json".format(package_name)
            )
            if not result.status_code == 200:
                return None
            result = json.loads(result.content.decode("utf-8"))
            return result["info"]["version"]
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
        if hasattr(request, "root") and request.root is not None:
            root = request.root
        else:
            root = repository_root_factory(request)
        return (
            root[name]
            if name in [package.__name__ for package in root]
            else None
        )

    def get_last_release(self):
        if not len(self):
            return None
        elif len(self) == 1:
            return list(self)[0]
        max_version = max(
            [parse_version(version) for version in self.releases.keys()]
        )
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

    def __json__(self, request):
        serializer = PackageListSerializer()
        return serializer.serialize(self)


class Release(SubscriptableMixin, ClonableModelMixin, Model):
    _subobjects_attr = "release_files"
    _parent_name = "package"
    _name_attribute = "version"

    def __init__(
        self,
        version,
        metadata={},
        deserialize_metadata=True,
        package=None,
        **kwargs,
    ):
        self.release_files = MyOOBTree()
        self.version = version
        self.package = package
        self.original_metadata = metadata or {}
        if deserialize_metadata:
            schema = Metadata()
            self.metadata = schema.serialize(self.original_metadata)
            self.metadata = schema.deserialize(self.metadata)
        super().__init__(
            name=version,
            metadata=metadata,
            deserialize_metadata=True,
            package=package,
            **kwargs,
        )

    def __getitem__(self, version_or_index):
        try:
            if isinstance(version_or_index, int):
                return next(
                    itertools.islice(
                        self.__iter__(), version_or_index, version_or_index + 1
                    )
                )
            return self.release_files[version_or_index]
        except (KeyError, IndexError, StopIteration):
            return None

    def __setitem__(self, key, value):
        key = self.format_key(key)
        self.release_files[key] = value

    @classmethod
    def by_packagename(cls, package_name, request):
        root = repository_root_factory(request)
        if package_name not in [pkg.__name__ for pkg in root]:
            return None
        return list(root[package_name].releases.values())

    @classmethod
    def by_releasename(cls, package_name, release, request):
        if hasattr(request, "root") and request.root is not None:
            root = request.root
        else:
            root = repository_root_factory(request)
        if package_name in [pkg.__name__ for pkg in root]:
            return root[package_name].get(release, None)

    def __json__(self, request):
        return ReleaseAPISerializer(request).serialize(self)


class ReleaseFile(ClonableModelMixin, Model):
    _path = None
    _packages_directory = None
    _release_file_directory = None
    __parent__ = None
    _parent_name = "release"
    _name_attribute = "filename"

    def __init__(
        self,
        filename,
        content,
        md5_digest=None,
        status=None,
        release=None,
        **kwargs,
    ):
        self.uuid = uuid.uuid4()
        self.filename = filename
        self.release = release
        self.md5_digest = md5_digest
        self.set_content(content)
        self.upload_date = datetime.datetime.now(tz=utc)
        self.status = status if status is not None else STATUS.cached
        super().__init__(
            filename,
            content,
            md5_digest=md5_digest,
            status=status,
            release=release,
            **kwargs,
        )
        if release is not None:
            self.__parent__[self.format_key(self.__name__)] = self

    @property
    def __name__(self):
        return self.filename

    @property
    def __parent__(self):
        return self.release

    def _compute_release_file_directory(self):
        time_low = self.uuid.time_low
        path = list(map(lambda x: hex(int(x)), str(time_low)))
        return os.path.join(*path)

    def get_content_type(self, content):
        buf = io.BytesIO(content)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            self.content_type = m.id_buffer(buf.read())

    def _packages_directory(self):
        request = get_current_request()
        registry = request.registry if request else getGlobalSiteManager()
        settings = registry.getUtility(ISettings, name="settings")
        packages_directory = settings.get("papaye").get("packages_directory")
        if not packages_directory:
            raise ConfigurationError(
                "packages_directory must be correcly configured"
            )
        return packages_directory

    def set_content(self, content):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "wb") as release_file:
            release_file.write(content)
            self.relative_path = self._compute_release_file_directory()
            self.size = len(content)
            self.content_type = self.get_content_type(content)

    @property
    def path(self):
        if not self._path:
            try:
                packages_directory = self._packages_directory()
                release_file_directory = self._compute_release_file_directory()
                self._path = os.path.join(
                    packages_directory, release_file_directory
                )
            except Exception:
                return None
        return os.path.join(self._path, self.filename)

    @path.setter
    def set_path(self, path):
        self._path = path

    @property
    def full_path(self):
        try:
            return os.path.join(self._packages_directory(), self.path)
        except:
            return None

    @classmethod
    def clone(cls, model_obj):
        """Return a clone on given object"""
        clone = cls.__new__(cls)
        clone.filename = model_obj.filename
        clone.md5_digest = model_obj.md5_digest
        clone.size = model_obj.size
        clone._path = model_obj._path
        clone.upload_date = copy.copy(model_obj.upload_date)
        clone.content_type = model_obj.content_type
        clone.status = model_obj.status
        return clone

    @classmethod
    def by_releasefilename(cls, package, release, releasefile, request):
        if hasattr(request, "root") and request.root is not None:
            root = request.root
        else:
            root = repository_root_factory(request)
        if package in [pkg.__name__ for pkg in root] and root[package].get(
            release
        ):
            return root[package][release].get(releasefile, None)

    def format_key(self, key):
        return pkg_resources.safe_name(key.lower())


class User(Model):
    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = self.hash_password(password)
        self.groups = kwargs.get("groups", [])

    def hash_password(self, password):
        return hashlib.sha512(password.encode("utf-8")).hexdigest()

    def password_verify(self, clear_password):
        return self.hash_password(clear_password) == self.password

    def __repr__(self):
        return '<{}.{} "{}" at {}>'.format(
            self.__module__, self.__class__.__name__, self.username, id(self)
        )

    @classmethod
    def by_username(cls, username, request):
        """Return user instance by username"""
        root = user_root_factory(request)
        if username in [user.username for user in root]:
            return root[username]
        return None

    def __json__(self, *args, **kwargs):
        request = args[0]
        return {
            "username": self.username,
            "url": request.url,
            "groups": self.groups,
        }


class RestrictedContext(object):
    def __acl__(self):
        return [(Allow, "user", "view")]


class Application(object):
    def __acl__(self):
        return [(Allow, Authenticated, "view")]
