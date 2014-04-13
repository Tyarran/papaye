import io
import json
import logging
import magic
import requests
import hashlib

from beaker.cache import cache_region
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from pkg_resources import parse_version
from requests.exceptions import ConnectionError
from ZODB.blob import Blob
from pyramid.security import Allow, ALL_PERMISSIONS

from papaye.factories import user_root_factory


logger = logging.getLogger(__name__)


class Root(OOBTree):
    __name__ = __parent__ = None
    __acl__ = [
        (Allow, 'group:installer', 'install'),
        (Allow, 'group:admin', ALL_PERMISSIONS)
    ]


class Package(Persistent):

    def __init__(self, name):
        self.__name__ = name
        self.name = name
        self.releases = OOBTree()

    def __getitem__(self, release_name):
        return self.releases[release_name]

    def __setitem__(self, key, value):
        self.releases[key] = value

    @cache_region('pypi', 'get_last_remote_filename')
    def get_last_remote_version(self, proxy):
        logger.debug('Not in cache')
        if not proxy:
            return None
        try:
            result = requests.get('http://pypi.python.org/pypi/{}/json'.format(self.__name__))
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


class Release(Persistent):

    def __init__(self, name, version):
        self.__name__ = name
        self.release_files = OOBTree()
        self.version = version

    def __getitem__(self, release_file_name):
        return self.release_files[release_file_name]

    def __setitem__(self, key, value):
        self.release_files[key] = value


class ReleaseFile(Persistent):

    def __init__(self, filename, content, md5_digest=None):
        self.filename = filename
        self.__name__ = filename
        self.content = Blob(content)
        self.content_type = self.get_content_type(content)
        self.md5_digest = md5_digest

    def get_content_type(self, content):
        buf = io.BytesIO(content)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            self.content_type = m.id_buffer(buf.read())


class User(Persistent):

    def __init__(self, username, password):
        self.username = username
        self.password = self.hash_password(password)

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
