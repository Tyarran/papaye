import logging

from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPConflict,
    HTTPNotFound,
    HTTPUnauthorized,
    HTTPTemporaryRedirect
)
from pyramid.response import Response
from pyramid.security import forget
from pyramid.view import view_config, notfound_view_config, forbidden_view_config

from papaye.models import ReleaseFile, Package, Release, Root
from papaye.proxy import PyPiProxy
from papaye.views.commons import BaseView
from papaye.tasks.download import download_release_from_pypi


logger = logging.getLogger(__name__)


@forbidden_view_config()
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


@notfound_view_config(route_name="simple", renderer='simple.jinja2')
def not_found(request):
    settings = request.registry.settings
    proxy = settings.get('papaye.proxy', False)
    proxy = True if proxy and proxy == 'true' else False
    if not proxy:
        return HTTPNotFound()
    try:
        proxy = PyPiProxy(request, request.matchdict['traverse'][0])
        package = proxy.build_repository()
        if not package:
            return HTTPNotFound()
        if len(request.matchdict['traverse']) == 1:
            view = ListReleaseFileView(package, request)
        elif len(request.matchdict['traverse']) == 2:
            context = package[request.matchdict['traverse'][1]]
            view = ListReleaseFileByReleaseView(context, request)
        elif len(request.matchdict['traverse']) == 3:
            release_file = package[request.matchdict['traverse'][1]][request.matchdict['traverse'][2]]
            package_name, release_name, _ = request.matchdict['traverse']
            download_release_from_pypi.delay(package_name, release_name)
            return HTTPTemporaryRedirect(location=release_file.pypi_url)
    except KeyError:
        return HTTPNotFound()
    return view()


@view_config(
    context="papaye.models.Root",
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    permission="install"
)
class ListPackagesView(BaseView):

    def __call__(self):
        return {
            'objects': ((self.request.resource_url(package, route_name=self.request.matched_route.name), package)
                        for package in self.context.values()),
        }


@view_config(
    context=Package,
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    permission='install'
)
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
        if package.repository_is_up_to_date(Package.get_last_remote_version(self.proxy, package.name)):
            return context
        else:
            return not_found(self.request)


@view_config(
    context=Release,
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    permission='install'
)
class ListReleaseFileByReleaseView(BaseView):

    def __call__(self):
        return {
            'objects': (
                (self.request.resource_url(release_file, route_name=self.request.matched_route.name), release_file)
                for release_file in self.context.release_files.values()),
        }


@view_config(context=ReleaseFile, route_name="simple", permission='install', request_method="GET")
class DownloadReleaseView(BaseView):

    def __call__(self):
        check_update = True if self.request.GET.get('check_update', 'true') == 'true' else False
        package = self.context.__parent__.__parent__
        last_remote_version = Package.get_last_remote_version(self.proxy, package.name)
        if check_update:
            if not package.repository_is_up_to_date(last_remote_version):
                return not_found(self.request)
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
        post = dict(self.request.POST)
        metadata = dict([(key, value) for key, value in post.items() if key != 'content'])
        if post.get(':action') == "file_upload":
            name = post.get('name')
            version = post.get('version')
            content = post.get('content')
            md5_digest = post.get('md5_digest')

            package = self.context[name] if self.context.get(name) else Package(name)
            package.__parent__ = self.context
            self.context[name] = package

            release = package[version] if package.releases.get(version) else Release(name=version,
                                                                                     version=version,
                                                                                     metadata=metadata)
            release.__parent__ = package
            self.context[name][version] = release

            if release.release_files.get(content.filename):
                return HTTPConflict()

            release_file = ReleaseFile(filename=content.filename, content=content.file.read(), md5_digest=md5_digest)
            release = self.context[name][version]
            self.context[name][version][content.filename] = release_file
            return Response()
        else:
            return HTTPBadRequest()
