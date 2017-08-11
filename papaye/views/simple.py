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
from pyramid.view import (
    view_config, notfound_view_config, forbidden_view_config
)

from papaye.models import ReleaseFile, Package, Release, Root, STATUS
from papaye.proxy import PyPiProxy
from papaye.views.commons import BaseView
from papaye.tasks.download import download_release_from_pypi


logger = logging.getLogger(__name__)


@forbidden_view_config()
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.extend(forget(request))
    return response


def proxy_activated(settings):
    proxy = settings.get('papaye.proxy', False)
    return True if proxy and proxy == 'true' else False


def parse_matchdict(matchdict):
    entities = ('package', 'release', 'release_file')
    traversed = matchdict['traverse']
    result = {}
    if len(traversed):
        desired_entity = entities[len(traversed) - 1]
        result = {
            'desired_entity': desired_entity,
        }
        for index, entity in enumerate(entities):
            if index < len(traversed):
                result[entity] = traversed[index]

    return result


@notfound_view_config(route_name="simple", renderer='simple.jinja2')
def not_found(request, stop=None):
    if not proxy_activated(request.registry.settings) or stop is not None:
        return HTTPNotFound()
    proxy = PyPiProxy()
    parsed = parse_matchdict(request.matchdict)
    package_name = parsed['package']
    if package_name in request.root:
        local_package = request.root[package_name]
    else:
        local_package = Package(package_name)
        local_package.fake = True

    merged_repository = proxy.merged_repository(local_package)

    if merged_repository:
        package = merged_repository[package_name]
        if parsed['desired_entity'] == 'package':
            view = ListReleaseFileView(package, request)
            view.stop = True
        elif parsed['desired_entity'] == 'release':
            context = package[request.matchdict['traverse'][1]]
            view = ListReleaseFileByReleaseView(context, request)
        elif parsed['desired_entity'] == 'release_file':
            release_file = package[parsed['release']][parsed['release_file']]
            filename = request.matchdict['traverse'][2]
            package_name, release_name, _ = request.matchdict['traverse']
            download_release_from_pypi.delay(
                request.registry._zodb_databases[''],
                package_name,
                release_name,
                filename,
            )
            return HTTPTemporaryRedirect(location=release_file.pypi_url)
        return view()
    return HTTPNotFound()


@view_config(
    context="papaye.models.Root",
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    # permission="install"
)
class ListPackagesView(BaseView):

    def __call__(self):
        return {
            'objects': ((self.request.resource_url(
                package,
                route_name=self.request.matched_route.name
            ), package) for package in list(self.context)),
        }


@view_config(
    context=Package,
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    # permission='install'
)
class ListReleaseFileView(BaseView):
    _repository = None

    def __init__(self, context, request):
        super().__init__(context, request)
        self.proxy_instance = PyPiProxy()
        self.stop = hasattr(self, 'stop') and self.stop

    @property
    def repository(self):
        if self._repository is None:
            if self.stop:
                self._repository = self.context.root
            else:
                self._repository = self.proxy_instance.merged_repository(
                    self.context
                )
        return self._repository

    def __call__(self):
        package = self.context
        root = package.root
        if self.repository is not root:
            self.repository.name = root.name
        rfiles = [
            rfile for rel in self.repository[package.name]
            for rfile in rel
        ]
        context = {
            'objects': (self.format_release_file(rfile) for rfile in rfiles)
        }
        transaction.abort()
        if len(rfiles):
            return context
        elif self.stop:
            return HTTPNotFound()
        else:
            return not_found(self.request)

    def format_release_file(self, release_file):
        return self.request.resource_url(
            release_file,
            route_name='simple'
        )[:-1] + "#md5={}".format(release_file.md5_digest), release_file


@view_config(
    context=Release,
    route_name="simple",
    renderer="simple.jinja2",
    request_method="GET",
    # permission='install'
)
class ListReleaseFileByReleaseView(BaseView):

    def __call__(self):
        return {
            'objects': (
                (self.request.resource_url(release_file, route_name=self.request.matched_route.name), release_file)
                for release_file in self.context.release_files.values()),
        }


@view_config(context=ReleaseFile, route_name="simple", request_method="GET")
# @view_config(context=ReleaseFile, route_name="simple", permission='install', request_method="GET")
class DownloadReleaseView(BaseView):

    def __call__(self):
        url = self.request.static_url(self.context.full_path)
        response = HTTPTemporaryRedirect(location=url)
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
            package.root = self.context
            self.context[name] = package

            release = package[version] if package.releases.get(version) else Release(version=version,
                                                                                     metadata=metadata)
            release.package = package
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
