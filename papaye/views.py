import json
import logging
import requests

from beaker.cache import cache_region
from CodernityDB.database import RecordNotFound
from os import mkdir
from os.path import join, exists
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect, HTTPBadRequest, HTTPConflict, HTTPUnauthorized
from pyramid.response import FileResponse, Response
from pyramid.security import forget
from pyramid.view import view_config, forbidden_view_config
from requests import ConnectionError


SUPPORTED_PACKAGE_FORMAT = (
    '.egg',
    '.tar.gz',
    '.whl',
    '.zip',
    '.gz',
)


LOG = logging.getLogger(__name__)


def is_supported_package_format(filename):
    for e in SUPPORTED_PACKAGE_FORMAT:
        if filename.endswith(e):
            return e
    return None


class SimpleView(object):

    def __init__(self, request):
        LOG.debug('Dispatch "{}" route as {} with {} method'.format(
            request.matched_route.name,
            request.path,
            request.method
        ))
        self.request = request
        self.settings = request.registry.settings
        self.repository = self.settings.get('papaye.repository')
        proxy = self.settings.get('papaye.proxy', False)
        self.proxy = proxy == 'true' if proxy else False
        self.db = self.request.db

    @view_config(route_name="simple", renderer="simple.jinja2", permission='install', request_method="GET")
    def list_packages(self):
        packages = (elem['doc'] for elem in self.db.all('package', with_doc=True))
        return {'objects': packages, 'root_url': self.request.route_url('simple')}

    @cache_region('pypi', 'get_last_remote_filename')
    def get_last_remote_release(self, package):
        LOG.debug('Not in cache')
        if not self.proxy:
            return None
        try:
            result = requests.get('http://pypi.python.org/pypi/{}/json'.format(package['name']))
            if result.status_code == 404:
                return None
            result = json.loads(result.content)
            for url in result['urls']:
                if url['packagetype'] == 'sdist':
                    return url['filename']
        except ConnectionError:
            pass
        return None

    def repository_is_up_to_date(self, last_remote_release, package_name):
        if not last_remote_release:
            return True
        releases = self.db.get_many('rel_release_package', package_name, with_doc=True)
        if len([release for release in releases if last_remote_release == release['doc']['name']]):
            return True
        else:
            return False

    def package_not_found(self, package_name, message='Package "{}" not found'):
        LOG.info(message.format(package_name))
        if self.proxy:
            LOG.info('Proxify "{}" package'.format(package_name))
            return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/'.format(package_name))
        else:
            return HTTPNotFound('Package doesn\'t exists')

    def release_not_found(self, package_name, release_name, message='Release "{}" for package "{}" not found'):
        message = message.format(release_name, package_name)
        LOG.info(message)
        if self.proxy:
            LOG.info('Proxify "{}" release for package "{}"'.format(release_name, package_name))
            return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/{}/'.format(package_name, release_name))
        else:
            return HTTPNotFound('Release doesn\'t exists')

    @view_config(route_name="simple_release", renderer="simple.jinja2", permission='install')
    def list_releases(self):
        package_name = self.request.matchdict['package']
        if self.db.count(self.db.get_many, 'package', package_name):
            package = self.db.get('package', package_name, with_doc=True)['doc']
            last_remote_release = self.get_last_remote_release(package)
            if not self.repository_is_up_to_date(last_remote_release, package_name):
                message = 'Package "{}" is outdated. Request redirect to Pypi'
                return self.package_not_found(package_name, message=message)
            else:
                releases = self.db.get_many('rel_release_package', package_name, with_doc=True)
                releases_gen = (release['doc'] for release in releases)
                return {'objects': releases_gen, 'package': package}

        else:
            return self.package_not_found(package_name)

    @view_config(route_name="download_release", permission='install')
    def download_release(self):
        package = self.request.matchdict['package']
        release = self.request.matchdict['release']
        if len(release.split('-')) > 1:
            file_path = join(self.repository, package, release)
        else:
            file_path = join(self.repository, package, '{}-{}.{}'.format(release, package, 'tar.gz'))
        if exists(file_path):
            return FileResponse(file_path)
        else:
            message = 'Release "{}" for package "{}" not found'
            LOG.info(message)
            return self.release_not_found(package, release)

    @view_config(route_name="simple", permission='publish', request_method='POST')
    def upload_release(self):
        response = HTTPBadRequest()
        if not 'content' in self.request.POST:
            return response
        filename = self.request.POST['content'].filename
        ext = is_supported_package_format(filename)
        if ext:
            package = filename.split(ext)[0].split('-')[0]
            directory = join(self.repository, package)
            path = join(directory, filename)
            try:
                package_doc = self.db.get('package', package, with_doc=True)
            except RecordNotFound:
                package_doc = {'type': 'package', 'name': package}
                self.db.insert(package_doc)
            if not exists(directory):
                mkdir(directory)
            with open(path, 'wb') as release_file:
                if self.db.count(self.db.get_many, 'release', filename):
                    return HTTPConflict()
                release_doc = {'type': 'release', 'package': package, 'name': filename}
                self.db.insert(release_doc)
                release_file.write(self.request.POST['content'].file.read())
            return Response()
        return response


@forbidden_view_config()
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response
