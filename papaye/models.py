import datetime
import hashlib
import io
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
from repoze.evolution import ZODBEvolutionManager
from requests.exceptions import ConnectionError
from pytz import utc

from papaye.factories import user_root_factory, repository_root_factory, APP_ROOT_NAME
from papaye.schemas import Metadata


logger = logging.getLogger(__name__)
SW_VERSION = 1


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


class Root(OOBTree):
    __name__ = __parent__ = None

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

    def __getitem__(self, package_name):
        keys = [key for key in self.keys()
                if format_key(key) == format_key(package_name)]
        if len(keys) == 1:
            return self.get(keys[0])


class Package(Persistent):
    pypi_url = 'http://pypi.python.org/pypi/{}/json'

    def __init__(self, name):
        self.__name__ = name
        self.name = name
        self.releases = OOBTree()

    def __getitem__(self, release_name):
        return self.releases[release_name]

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
        root = repository_root_factory(request)
        return root[name] if name in root else None

    def get_last_release(self):
        max_version = max([parse_version(version) for version in self.releases.keys()])
        for version, release in self.releases.items():
            if parse_version(version) == max_version:
                return release


class Release(Persistent):

    def __init__(self, name, version, metadata):
        self.__name__ = name
        self.release_files = OOBTree()
        self.version = version
        self.original_metadata = metadata
        self.metadata = Metadata().deserialize(metadata)

    def __getitem__(self, release_file_name):
        return self.release_files[format_key(release_file_name)]

    def __setitem__(self, key, value):
        key = format_key(key)
        self.release_files[key] = value
        self.release_files[key].__parent__ = self

    @classmethod
    def by_packagename(cls, package, request):
        root = repository_root_factory(request)
        if package not in root:
            return None
        return list(root[package].releases.values())


class ReleaseFile(Persistent):

    def __init__(self, filename, content, md5_digest=None):
        self.filename = self.__name__ = filename
        self.md5_digest = md5_digest
        self.set_content(content)
        self.upload_date = datetime.datetime.now(tz=utc)

    def get_content_type(self, content):
        buf = io.BytesIO(content)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            self.content_type = m.id_buffer(buf.read())

    def set_content(self, content):
        self.content = Blob(content)
        self.content_type = self.get_content_type(content)
        self.size = len(content)


class User(Persistent):

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = self.hash_password(password)
        self.groups = kwargs.get('groups', [])

    def hash_password(self, password):
        return hashlib.sha512(password.encode('utf-8')).hexdigest()

    def password_verify(self, clear_password):
        return self.hash_password(clear_password) == self.password

    @classmethod
    def by_username(cls, username, request):
        """Return user instance by username"""
        root = user_root_factory(request)
        if username not in root:
            return None
        else:
            return root[username]
