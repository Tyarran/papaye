import logging

from os import listdir
from os.path import isdir, join, exists
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.response import FileResponse
from pyramid.view import view_config


SUPPORTED_PACKAGE_FORMAT = (
    '.egg',
    '.tar.gz',
    '.whl',
    '.zip',
)

LOG = logging.getLogger(__name__)


class PackageNotFoundException(Exception):

    def __init__(self, message, redirect_to, package):
        super(PackageNotFoundException, self).__init__(message)
        self.redirect_to = redirect_to
        self.package = package


class ReleaseNotFoundException(PackageNotFoundException):

    def __init__(self, message, redirect_to, package, release):
        super(ReleaseNotFoundException, self).__init__(message, redirect_to, package)
        self.release = release


@view_config(route_name="simple", renderer="simple.jinja2")
@view_config(route_name="simple_release", renderer="simple.jinja2")
@view_config(route_name="download_release")
class SimpleView(object):

    def __init__(self, request):
        LOG.debug('Dispatch {} route as {}'.format(request.matched_route.name, request.path))
        self.request = request
        self.settings = request.registry.settings
        self.repository = self.settings.get('papaye.repository')
        self.proxy = self.settings.get('papaye.proxy', False)

    def list_packages(self):
        return ((e, self.request.route_path('simple', e))
                for e in sorted(listdir(self.repository))
                if isdir(join(self.repository, e)))

    def list_releases(self):
        package = self.request.matchdict['package']
        package_dir = join(self.repository, package)
        if exists(package_dir):
            releases_gen = ((e, self.request.route_path('simple', package, e))
                            for e in sorted(listdir(join(self.repository, package)))
                            if not isdir(join(self.repository, package, e))
                            and e[-3:] in SUPPORTED_PACKAGE_FORMAT
                            or e[-7:] in SUPPORTED_PACKAGE_FORMAT)
            return releases_gen, package
        else:
            message = 'Package "{}" not found'.format(package)
            LOG.info(message)
            raise PackageNotFoundException(
                message,
                redirect_to='http://pypi.python.org/simple/{}/'.format(package),
                package=package,
            )

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
            raise ReleaseNotFoundException(
                message,
                redirect_to='http://pypi.python.org/simple/{}/{}/'.format(package, release),
                package=package,
                release=release,
            )

    def __call__(self):
        try:
            if self.request.matched_route.name == 'simple':
                return {'objects': self.list_packages()}
            elif self.request.matched_route.name == 'simple_release':
                objs, package = self.list_releases()
                return {'objects': objs, 'package': package}
            else:
                return self.download_release()
        except PackageNotFoundException as ex:
            if self.proxy:
                LOG.info('Proxify "{}" package'.format(ex.package))
                return HTTPTemporaryRedirect(ex.redirect_to)
            else:
                return HTTPNotFound('Package doesn\'t exists')
        except ReleaseNotFoundException as ex:
            if self.proxy:
                LOG.info('Proxify "{}" release for package "{}"'.format(ex.release, ex.package))
                return HTTPTemporaryRedirect(ex.redirect_to)
            else:
                return HTTPNotFound('Release doesn\'t exists')
