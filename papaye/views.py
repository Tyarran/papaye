import json
import logging
import requests

from beaker.cache import cache_region
from os import listdir
from os.path import isdir, join, exists
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.response import FileResponse
from pyramid.view import view_config
from requests import ConnectionError


SUPPORTED_PACKAGE_FORMAT = (
    '.egg',
    '.tar.gz',
    '.whl',
    '.zip',
)

LOG = logging.getLogger(__name__)


class SimpleView(object):

    def __init__(self, request):
        LOG.debug('Dispatch "{}" route as {}'.format(request.matched_route.name, request.path))
        self.request = request
        self.settings = request.registry.settings
        self.repository = self.settings.get('papaye.repository')
        self.proxy = self.settings.get('papaye.proxy', False)

    @view_config(route_name="simple", renderer="simple.jinja2")
    def list_packages(self):
        packages = ((e, self.request.route_path('simple', e))
                    for e in sorted(listdir(self.repository))
                    if isdir(join(self.repository, e)))
        return {'objects': packages}

    @cache_region('pypi', 'get_last_remote_filename')
    def get_last_remote_release(self, package):
        LOG.debug('Not in cache')
        try:
            result = requests.get('http://pypi.python.org/pypi/{}/json'.format(package))
            if result.status_code == 404:
                return None
            result = json.loads(result.content)
            for url in result['urls']:
                if url['packagetype'] == 'sdist':
                    return url['filename']
        except ConnectionError:
            pass
        return None

    def repository_is_up_to_date(self, last_remote_release, package_dir):
        if not last_remote_release:
            return True
        if last_remote_release in listdir(package_dir):
            return True
        else:
            return False

    def package_not_found(self, package, message='Package "{}" not found'):
        LOG.info(message.format(package))
        if self.proxy:
            LOG.info('Proxify "{}" package'.format(package))
            return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/'.format(package))
        else:
            return HTTPNotFound('Package doesn\'t exists')

    def release_not_found(self, package, release, message='Release "{}" for package "{}" not found'):
        message = message.format(release, package)
        LOG.info(message)
        if self.proxy:
            LOG.info('Proxify "{}" release for package "{}"'.format(release, package))
            return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/{}/'.format(package, release))
        else:
            return HTTPNotFound('Release doesn\'t exists')

    @view_config(route_name="simple_release", renderer="simple.jinja2")
    def list_releases(self):
        package = self.request.matchdict['package']
        package_dir = join(self.repository, package)
        if exists(package_dir):
            last_remote_release = self.get_last_remote_release(package)
            if not self.repository_is_up_to_date(last_remote_release, package_dir):
                message = 'Package "{}" is outdated. Request redirect to Pypi'.format(package)
                return self.package_not_found(package, message=message)
            else:
                releases_gen = ((e, self.request.route_path('simple', package, e))
                                for e in sorted(listdir(join(self.repository, package)))
                                if not isdir(join(self.repository, package, e))
                                and e[-3:] in SUPPORTED_PACKAGE_FORMAT
                                or e[-7:] in SUPPORTED_PACKAGE_FORMAT)
                return {'objects': releases_gen, 'package': package}
        else:
            return self.package_not_found(package)

    @view_config(route_name="download_release")
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
            message = 'Release "{}" for package "{}" not found'.format(release, package)
            LOG.info(message)
            return self.release_not_found(package, release)
