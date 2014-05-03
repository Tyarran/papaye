import json
import requests

# from pyramid.threadlocal import get_current_request
from requests.exceptions import ConnectionError

from papaye.factories import repository_root_factory
from papaye.models import Package, Release, ReleaseFile


class PyPiProxy:
    pypi_url = 'http://pypi.python.org/pypi/{}/json'

    def __init__(self, request,  package_name):
        self.request = request
        self.package_name = package_name
        self.url = self.pypi_url.format(package_name)

    def get_remote_informations(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                None
        except ConnectionError:
            return None

    def build_repository(self):
        root = repository_root_factory(self.request)
        info = self.get_remote_informations()
        if info:
            package = Package(info['info']['name'])
            package.__parent__ = root

            for remote_release in info['releases'].keys():
                release = Release(remote_release, remote_release)
                package[remote_release] = release
                for remote_release_file in info['releases'][remote_release]:
                    filename = remote_release_file['filename']
                    md5_digest = remote_release_file['md5_digest']
                    release_file = ReleaseFile(filename, b'', md5_digest)
                    release[filename] = release_file
            return package
        return None
