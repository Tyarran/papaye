import json
import logging
import urllib

from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPConflict,
    HTTPForbidden,
    HTTPNotFound,
    HTTPTemporaryRedirect,
    HTTPUnauthorized,
)
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import forget
from pyramid.view import view_config, notfound_view_config, forbidden_view_config

from papaye.views.commons import BaseView
from papaye.views.mixins import ExistsOnPyPIMixin
from papaye.models import ReleaseFile, Package, Release, Root


logger = logging.getLogger(__name__)


@forbidden_view_config()
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


@notfound_view_config(route_name="simple")
def not_found_view_dispatcher(request):
    if len(request.traversed) == 0:
        view = PackageNotFoundView(request, 'Package')
    elif len(request.traversed) == 1 and len(request.matchdict['traverse']) == 2:
        view = ReleaseNotFoundView
        return render_to_response('simple.jinja2', view(request, 'Release')())
    elif len(request.traversed) == 2 and len(request.matchdict['traverse']) == 3:
        view = ReleaseFileNotFoundView(request, 'File')
    else:
        return HTTPNotFound()
    return view()


class PackageNotFoundView(ExistsOnPyPIMixin, BaseView):
    pypi_url = 'http://pypi.python.org/simple/{}/'

    def __init__(self, request, type_name, context=None):
        self.type_name = type_name
        super().__init__(context, request)

    def make_redirection(self, final_url, response):
        logger.info('Proxify request to {}'.format(final_url))
        return HTTPTemporaryRedirect(final_url)

    def get_params(self):
        return (self.request.matchdict['traverse'][0], )

    def __call__(self):
        logger.info('{} "{}" not found in Papaye index'.format(
            self.type_name,
            self.request.matchdict['traverse'][0])
        )
        if self.proxy:
            pypi_url = self.pypi_url.format(*self.get_params())
            result = self.exists_on_pypi(pypi_url)
            if result:
                return self.make_redirection(pypi_url, result)
            else:
                logger.info('Not found on Pypi index')
                return HTTPNotFound()
        else:
            logger.info('Not found on Pypi index')
            return HTTPNotFound()


@view_config(renderer='simple.jinja2')
class ReleaseNotFoundView(PackageNotFoundView):
    pypi_url = 'http://pypi.python.org/pypi/{}/{}/json'

    def get_params(self):
        return self.request.matchdict['traverse'][:2]

    def make_redirection(self, final_url, response):
        logger.info('Get release files from {}'.format(final_url))
        result = json.loads(response.content.decode('utf-8'))
        objects = []
        for url in result.get('urls', []):
            release_file = ReleaseFile(url.get('filename'), b'')
            objects.append((url.get('url'), release_file))
        return {'objects': objects}


class ReleaseFileNotUpToDateView(ReleaseNotFoundView):
    pypi_url = 'https://pypi.python.org/pypi/{}/json'

    def get_params(self):
        return (self.request.matchdict['traverse'][0], )

    def format_url(self, url):
        split_result = url.split('#')
        base_url = split_result[0]
        md5 = split_result[1] if len(split_result) == 2 else None
        base_url += '?{}'.format(urllib.parse.urlencode({'check_update': 'false'}))
        if md5:
            base_url += '#{}'.format(md5)
        return base_url

    def make_redirection(self, final_url, response):
        context = super().make_redirection(final_url, response)
        objects = context['objects'] + [(self.format_url(url), elem) for url, elem in self.context['objects']]

        context['objects'] = (obj for obj in objects)
        return context


class ReleaseFileNotFoundView(ReleaseNotFoundView):
    pypi_url = 'http://pypi.python.org/pypi/{}/{}/json'

    def get_params(self):
        return self.request.matchdict['traverse'][:2]

    def make_redirection(self, final_url, response):
        result = json.loads(response.content.decode('utf-8'))
        url = [url['url'] for url
               in result['urls'] if url.get('filename') == self.request.matchdict['traverse'][-1]]
        url = url[0] if url else None
        if not url:
            return HTTPNotFound()
        logger.info('Proxy request to {}'.format(url))
        return HTTPTemporaryRedirect(url)


@view_config(context="papaye.models.Root",
             route_name="simple",
             renderer="simple.jinja2",
             request_method="GET",
             permission="install")
class ListPackagesView(BaseView):

    def __call__(self):
        return {
            'objects': ((self.request.resource_url(package, route_name=self.request.matched_route.name), package)
                        for package in self.context.values()),
        }


@view_config(context=Package,
             route_name="simple",
             renderer="simple.jinja2",
             request_method="GET",
             permission='install')
class ListReleaseFileView(BaseView):

    def __call__(self):
        package = self.context
        release_files = []
        for release in package.releases.values():
            for release_file in release.release_files.values():
                release_files.append(release_file)
        context = {
            'objects': ((self.request.resource_url(
                release_file,
                route_name='simple'
            )[:-1] + "#md5={}".format(release_file.md5_digest), release_file) for release_file in release_files),
        }
        if package.repository_is_up_to_date(package.get_last_remote_version(self.proxy)):
            return context
        else:
            release_not_found_view = ReleaseFileNotUpToDateView(self.request, 'Release', context=context)
            release_not_found_view.proxy = self.proxy
            return release_not_found_view()


@view_config(context=Release, route_name="simple")
class ForbiddenView(BaseView):

    def __call__(self):
        return HTTPForbidden()


@view_config(context=ReleaseFile, route_name="simple", permission='install', request_method="GET")
class DownloadReleaseView(BaseView):

    def __call__(self):
        check_update = True if self.request.GET.get('check_update', 'true') == 'true' else False
        package = self.context.__parent__.__parent__
        last_remote_version = package.get_last_remote_version(self.proxy)
        if check_update:
            if not package.repository_is_up_to_date(last_remote_version):
                return not_found_view_dispatcher(self.request)
        response = Response()
        response.content_disposition = 'attachment; filename="{}"'.format(self.context.filename)
        response.charset = 'utf-8'
        response.content_type = self.context.content_type
        response.body_file = self.context.content.open()
        return response


@view_config(context=Root, route_name="simple", request_method="POST", permission="add")
class UploadView():

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def __call__(self):
        if self.request.POST[':action'] == "file_upload":
            name = self.request.POST.get('name')
            version = self.request.POST.get('version')
            content = self.request.POST['content']
            md5_digest = self.request.POST.get('md5_digest')
            package = self.context[name] if self.context.get(name) else Package(name)
            package.__parent__ = self.context
            self.context[name] = package

            release = package[version] if package.releases.get(version) else Release(name=version, version=version)
            release.__parent__ = package
            self.context[name][version] = release

            if release.release_files.get(content.filename):
                return HTTPConflict()
            content.file.seek(0)
            release_file = ReleaseFile(filename=content.filename, content=content.file.read(), md5_digest=md5_digest)
            release_file.__parent__ = release
            self.context[name][version][content.filename] = release_file
            logger.info('File "{}" successfully added in repository')
            return Response()
        else:
            return HTTPBadRequest()
