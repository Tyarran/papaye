import logging
import pkg_resources
import transaction

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

from papaye.models import ReleaseFile, Package, Release, Root, STATUS
from papaye.proxy import PyPiProxy
from papaye.views.commons import BaseView
from papaye.tasks.download import download_release_from_pypi


logger = logging.getLogger(__name__)


@forbidden_view_config()
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


def proxy_activated(settings):
    proxy = settings.get('papaye.proxy', False)
    return True if proxy and proxy == 'true' else False


@notfound_view_config(route_name="simple", renderer='simple.jinja2')
def not_found(request, stop=None):
    if not proxy_activated(request.registry.settings) or stop is not None:
        return HTTPNotFound()
    proxy = PyPiProxy()
    package_name = request.matchdict['traverse'][0]
    local_package = request.root[package_name] if package_name in request.root else Package(package_name)
    merged_repository = proxy.merged_repository(local_package)

    package = merged_repository[package_name]
    traversed = len(request.matchdict['traverse'])
    if traversed == 1:
        view = ListReleaseFileView(package, request)
        view.stop = True
    elif traversed == 2:
        context = package[request.matchdict['traverse'][1]]
        view = ListReleaseFileByReleaseView(context, request)
    elif traversed == 3:
        release_file = package[request.matchdict['traverse'][1]][request.matchdict['traverse'][2]]
        filename = request.matchdict['traverse'][2]
        package_name, release_name, _ = request.matchdict['traverse']
        download_release_from_pypi.delay(request.registry._zodb_databases[''], package_name, release_name, filename)
        return HTTPTemporaryRedirect(location=release_file.pypi_url)
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
                        for package in list(self.context)),
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
        proxy = PyPiProxy()
        stop = hasattr(self, 'stop') and self.stop
        repository = package.__parent__ if stop else proxy.merged_repository(package)
        rfiles = [rfile for rel in repository[package.__name__] for rfile in rel]
        context = {'objects': ((self.request.resource_url(
            rfile,
            route_name='simple'
        )[:-1] + "#md5={}".format(rfile.md5_digest), rfile) for rfile in rfiles)}
        transaction.abort()
        if len(rfiles):
            return context
        elif stop:
            return HTTPNotFound()
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
        response = Response()
        response.content_disposition = 'attachment; filename="{}"'.format(self.context.filename)
        response.charset = 'utf-8'
        response.content_type = self.context.content_type
        response.body_file = self.context.content.open()
        response.content_length = self.context.size
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
            name = pkg_resources.safe_name(post.get('name'))
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

            release_file = ReleaseFile(
                filename=content.filename,
                content=content.file.read(),
                md5_digest=md5_digest,
                status=STATUS.local,
            )
            release = self.context[name][version]
            self.context[name][version][content.filename] = release_file
            return Response()
        else:
            return HTTPBadRequest()
