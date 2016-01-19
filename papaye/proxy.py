import hashlib
import json
import logging
import pickle
import requests

from ZODB.blob import Blob
from beaker.cache import cache_region
from requests.exceptions import ConnectionError

from papaye.models import Package, Release, ReleaseFile, Root


logger = logging.getLogger(__name__)


def clone(package):
    """Clone a package and his subobjects"""
    clone = pickle.loads(pickle.dumps(package))
    for release in clone:
        for rfile in release:
            rfile.content = Blob(package[release.__name__][rfile.__name__].content.open().read())
            assert hasattr(release, 'metadata')
    return clone


def smart_merge(repository_package, remote_package, root=None):
    """Merge package content into the given root if not exists"""
    merged_package = repository_package
    root = root if root is not None else Root()
    merged_package.__parent__ = root

    if remote_package is not None:
        existing_releases = list(merged_package.releases.keys())

        for release in remote_package:
            release_name = release.__name__
            if release_name not in existing_releases:
                merged_package[release_name] = release
            else:
                existing_release = merged_package[release_name]
                existing_release_files = list(merged_package[release_name].release_files.keys())
                for release_file in release:
                    if release_file.__name__ not in existing_release_files:
                        existing_release[release_file.__name__] = release_file
    root[merged_package.__name__] = merged_package
    return merged_package


@cache_region('pypi', 'download_file')
def download_file(filename, url, md5_digest):
    logger.info('Download file "{}"'.format(filename))
    result = requests.get(url)
    if result.status_code != 200:
        return None
    if md5_digest is not None and md5_digest != hashlib.md5(result.content).hexdigest():
        return None
    return result.content


class PyPiProxy:
    pypi_simple_url = 'https://pypi.python.org/simple/{}/'
    pypi_url = 'https://pypi.python.org/pypi/{}/json'

    @cache_region('pypi', 'get_remote_package_name')
    def get_remote_package_name(self, package_name):
        result = None
        try:
            response = requests.get(self.pypi_simple_url.format(package_name))
            if response.status_code == 200:
                result = response.url.split('/')[-2] if response.url.endswith('/') else response.url.split('/')[-1]
        except ConnectionError:
            pass
        return result

    @cache_region('pypi', 'get_remote_informations')
    def get_remote_informations(self, url):
        result = None
        try:
            response = requests.get(url)
            if response.status_code == 200:
                result = json.loads(response.content.decode('utf-8'))
        except ConnectionError:
            pass
        return result

    def build_remote_repository(self, package_name, release_name=None, metadata=False, content=False):
        package_name = self.get_remote_package_name(package_name)
        if package_name:
            info = self.get_remote_informations(self.pypi_url.format(package_name))
            package_root = Root()
            package = Package(info['info']['name'])
            package.__parent__ = package_root
            package_root[package.name] = package
            remote_releases = info['releases'].keys() if not release_name else [release_name, ]

            for remote_release in remote_releases:
                release = Release(
                    remote_release,
                    remote_release,
                    metadata=info['info'],
                    deserialize_metadata=metadata
                )
                package[remote_release] = release

                for remote_release_file in info['releases'][remote_release]:
                    filename = remote_release_file['filename']
                    md5_digest = remote_release_file['md5_digest']
                    if not content:
                        release_file = ReleaseFile(filename, b'', md5_digest)
                    else:
                        content_file = download_file(filename, remote_release_file['url'], md5_digest)
                        if content_file is not None:
                            release_file = ReleaseFile(filename, content_file, md5_digest)
                        else:
                            continue

                    setattr(release_file, 'pypi_url', remote_release_file['url'])
                    release[filename] = release_file
            return package_root
        return None

    def merged_repository(self, local_package, release_name=None, metadata=False, root=None):
        package_name = local_package.__name__
        remote_repository = self.build_remote_repository(package_name,
                                                         release_name=release_name,
                                                         metadata=metadata)
        remote_package = remote_repository[package_name] if remote_repository else None
        if getattr(local_package, 'fake', False) and not remote_repository:
            return None
        merged_package = smart_merge(local_package, remote_package, root=root)

        return merged_package.__parent__
