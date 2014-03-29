import datetime
import io
import json
import logging
import requests

from beaker.cache import cache_region
from os import mkdir
from os.path import join, exists
from pkg_resources import parse_version
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPConflict,
    HTTPNotFound,
    HTTPTemporaryRedirect,
    HTTPUnauthorized,
)
from pyramid.response import Response
from pyramid.security import forget
from pyramid.view import view_config, forbidden_view_config, notfound_view_config
from requests import ConnectionError

from papaye.models import Package, Release, ReleaseFile
from papaye.views.commons import BaseView


SUPPORTED_PACKAGE_FORMAT = (
    '.egg',
    '.tar.gz',
    '.whl',
    '.zip',
    '.gz',
)


logger = logging.getLogger(__name__)


def is_supported_package_format(filename):
    for e in SUPPORTED_PACKAGE_FORMAT:
        if filename.endswith(e):
            return e
    return None


@notfound_view_config(route_name="simple")
class NotFound(BaseView):
    request_types = ['package', 'release', 'release_file']

    def __init__(self, request, *args, **kwargs):
        super().__init__(None, request, *args, **kwargs)
        import ipdb; ipdb.set_trace()
        self.request = request
        self.requested_type = self.request_types[len(self.request.matchdict['traverse']) - 1]

    def __call__(self):
        element_name = self.request.matchdict['traverse'][self.request_types.index(self.requested_type)]
        if self.requested_type == 'package':
            return self._on_package_not_found(element_name)
        if self.requested_type == 'release':
            package_name = self.request.matchdict['traverse'][0]
            return self._on_release_not_found(package_name, element_name)
        else:
            message = 'File {} not found'.format(element_name)
            logger.warning(message)
            return HTTPNotFound('File "{}" doesn\'t exists'.format(element_name))

    def _on_package_not_found(self, package_name):
        logger.warning('Package "{}" not found'.format(package_name))
        if self.proxy:
            logger.info('Proxify "{}" package'.format(package_name))
            return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/'.format(package_name))
        else:
            return HTTPNotFound('Package doesn\'t exists')

    def _on_release_not_found(self, package_name, release_name):
        message = 'Release "{}" for package "{}" not found'.format(release_name, package_name)
        logger.warning(message)
        if self.proxy:
            logger.warning('Proxify "{}" release for package "{}"'.format(release_name, package_name))
            return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/{}/'.format(package_name, release_name))
        else:
            return HTTPNotFound('Release doesn\'t exists')


@view_config(context="BTrees.OOBTree.OOBTree", route_name="simple", renderer="simple.jinja2", request_method="GET")
class ListPackagesView(BaseView):

    def __call__(self):
        return {'objects': self.context.values(), 'root_url': self.request.current_route_url()}


@view_config(context="papaye.models.Package", route_name="simple", renderer="simple.jinja2", request_method="GET")
class ListReleaseView(BaseView):

    @cache_region('pypi', 'get_last_remote_filename')
    def get_last_remote_release(self, package):
        logger.debug('Not in cache')
        if not self.proxy:
            return None
        try:
            result = requests.get('http://pypi.python.org/pypi/{}/json'.format(package.__name__))
            if result.status_code == 404:
                return None
            result = json.loads(result.content)
            return result['info']['version']
        except ConnectionError:
            pass
        return None

    def repository_is_up_to_date(self, last_remote_release, package):
        if not last_remote_release:
            return True
        remote_version = parse_version(last_remote_release)

        local_versions = [release.version for release in package.releases.values()]
        for version in local_versions:
            if parse_version(version) >= remote_version:
                return True
        return False

    def __call__(self):
        package = self.context
        last_remote_release = self.get_last_remote_release(package)
        if not self.repository_is_up_to_date(last_remote_release, package):
            message = 'Package "{}" is outdated. Request redirect to Pypi'
            return self.package_not_found(package, message=message)
        else:
            return {
                'objects': ((self.request.current_route_url(e.__name__), e) for e in package.releases.values()),
                'type': 'release',
                'package': package.__name__,
            }


@view_config(
    context="papaye.models.ReleaseFile",
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    permission='install',
)
class DownloadReleaseView(BaseView):

    def __call__(self):
        chunk = io.StringIO(self.context.content.read())
        response = Response(app_iter=chunk)
        import ipdb; ipdb.set_trace()
        return response


#@view_config(route_name="simple", permission='publish', request_method='POST')
@view_config(route_name="simple", request_method='POST')
class UploadReleaseView(BaseView):

    def __call__(self):
        response = HTTPBadRequest()
        if not 'content' in data:
            return response
        filename = self.request.POST['content'].filename
        ext = is_supported_package_format(filename)
        if ext:
            package_name = self.request.POST['name']
            if not package_name in self.context:
                self.context[package_name] = Package(package_name)

            package = self.context[package_name]
            if self.request.POST['version'] in package:
                return HTTPConflict()
            version = self.request.POST['versions']
            filename = self.request.POST['filename']
            content = self.request.POST['content']
            package[version] = Release(version, version)
            release_file = ReleaseFile(
                filename,
                content.file.read()
            ) 
            package[version][filename] = release_file
            return Response()
        return response

# # @view_config(route_name="simple", permission='publish', request_method='POST')
# class UploadReleaseView(BaseView):

#     def release_not_found(self, package_name, release_name, message='Release "{}" for package "{}" not found'):
#         message = message.format(release_name, package_name)
#         LOG.info(message)
#         if self.proxy:
#             LOG.info('Proxify "{}" release for package "{}"'.format(release_name, package_name))
#             return HTTPTemporaryRedirect('http://pypi.python.org/simple/{}/{}/'.format(package_name, release_name))
#         else:
#             return HTTPNotFound('Release doesn\'t exists')

#     def __call__(self):
#         response = HTTPBadRequest()
#         if not 'content' in self.request.POST:
#             return response
#         filename = self.request.POST['content'].filename
#         ext = is_supported_package_format(filename)
#         if ext:
#             package = filename.split(ext)[0].split('-')[0]
#             directory = join(self.repository, package)
#             path = join(directory, filename)
#             try:
#                 package_doc = self.db.get('package', package, with_doc=True)
#             except RecordNotFound:
#                 package_doc = {'type': 'package', 'name': package}
#                 self.db.insert(package_doc)
#             if not exists(directory):
#                 mkdir(directory)
#             with open(path, 'wb') as release_file:
#                 if self.db.count(self.db.get_many, 'release', filename):
#                     return HTTPConflict()
#                 release_doc = {
#                     'type': 'release',
#                     'package': package,
#                     'name': filename,
#                     'upload_time': datetime.datetime.now().isoformat()
#                 }
#                 release_doc['info'] = dict(((key, value) for key, value in self.request.POST.iteritems()
#                                             if key != 'content' and key != ':action'))
#                 self.db.insert(release_doc)
#                 release_file.write(self.request.POST['content'].file.read())
#             return Response()
#         return response


@forbidden_view_config()
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response
