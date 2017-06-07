from cornice import Service
from pyramid.httpexceptions import HTTPNotFound
from pyramid.interfaces import ISettings
from cornice.validators import colander_validator

from papaye.factories.root import repository_root_factory

from .schemas import GetPackageSchema


packages = Service(
    name="packages",
    path="/api/compat/package/json",
    description="List package service",
    context='papaye.models.Root',
    factory=repository_root_factory,
    renderer='json_api_compat',
)
package = Service(
    name="package",
    path="/api/compat/package/{package_name}/json",
    description="Package service",
    factory=repository_root_factory,
    context="papaye.models.Package",
    traverse='{package_name}',
)
package_version = Service(
    name="package_by_version",
    path="/api/compat/package/{package_name}/{version}/json",
    description="Package service",
    factory=repository_root_factory,
)
package_version_filename = Service(
    name="filename_by_package_version",
    path="/api/compat/package/{package_name}/{version}/{filename}/json",
    description="Package service",
    factory=repository_root_factory,
)
vars = Service(
    name="vars",
    path="/api/compat/vars/json",
    description="Server variables",
)


@package.get(schema=GetPackageSchema(), validators=(colander_validator))
def get_package(request):
    return request.context.get_last_release()


@packages.get()
def list_packages(request):
    root = request.context
    return list(root)


@package_version.get(schema=GetPackageSchema(), validators=(colander_validator))
def get_package_by_version(request):
    package_name = request.validated['path']['package_name']
    version = request.validated['path']['version']
    packages = [package.__name__ for package in request.context]
    if package_name in packages:
        versions = request.context[package_name].releases.keys()
        if version in versions:
            return request.context[package_name][version]
    return HTTPNotFound()


@vars.get()
def get_variables(request):
    settings = request.registry.getUtility(ISettings)
    return {
        'repository_route_url': request.static_url(
            settings['papaye.packages_directory'] + '/'
        ),
        'simple_route_url': request.route_url('simple', traverse=''),
        'is_logged_url': request.route_url('islogged'),
        'login_route_url': request.route_url('login'),
        'logout_route_url': request.route_url('logout'),
    }
