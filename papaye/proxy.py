import copy
import json
import requests

from beaker.cache import cache_region
from requests.exceptions import ConnectionError

from papaye.factories import repository_root_factory
from papaye.models import Package, Release, ReleaseFile, Root


class PyPiProxy:
    pypi_simple_url = 'https://pypi.python.org/simple/{}/'
    pypi_url = 'https://pypi.python.org/pypi/{}/json'

    def __init__(self, request_or_dbconn,  package_name):
        self.request_or_dbconn = request_or_dbconn
        self.package_name = package_name

    @cache_region('pypi', 'get_remote_package_name')
    def get_remote_package_name(self, package_name):
        response = requests.get(self.pypi_simple_url.format(package_name))
        if response.status_code == 200:
            if response.url.endswith('/'):
                return response.url.split('/')[-2]
            else:
                return response.url.split('/')[-1]
        else:
            None

    @cache_region('pypi', 'get_remote_informations')
    def get_remote_informations(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                None
        except ConnectionError:
            return None

    def build_repository(self, release_name=None, with_metadata=False, root=None):
        root = repository_root_factory(self.request_or_dbconn) if root is None else root
        package_name = self.get_remote_package_name(self.package_name)
        if not package_name:
            return None
        info = self.get_remote_informations(self.pypi_url.format(package_name))
        if info:
            package = Package(info['info']['name'])
            package.__parent__ = root
            root[package.name] = package

            remote_releases = [release_name, ] if release_name else info['releases'].keys()

            for remote_release in remote_releases:
                release = Release(remote_release, remote_release, metadata=info['info'], deserialize_metadata=with_metadata)
                package[remote_release] = release

                for remote_release_file in info['releases'][remote_release]:
                    filename = remote_release_file['filename']
                    md5_digest = remote_release_file['md5_digest']
                    release_file = ReleaseFile(filename, b'', md5_digest)
                    setattr(release_file, 'pypi_url', remote_release_file['url'])
                    release[filename] = release_file
            return self.smart_merge(root, package)
        return None

    def smart_merge(self, root, package):
        if package.name not in root:
            return package
        else:
            merged_package = copy.copy(root[package.name])
            to_delete_releases_name = [release for release in package.releases.keys()
                                       if release in merged_package.releases.keys()]
            to_update_releases = [(key, value) for key, value in package.releases.items()
                                  if key not in to_delete_releases_name]
            merged_package.releases.update(to_update_releases)
            for release in merged_package:
                release.__parent__ = merged_package
            return merged_package
