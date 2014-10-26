from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from papaye.serializers import PackageListSerializer, PackageSerializer, ReleaseSerializer
from papaye.factories import repository_root_factory

packages = Service(
    name="packages",
    path="/api/package/json",
    description="List package service",
    factory=repository_root_factory
)
package = Service(
    name="package",
    path="/api/package/{package_name}/json",
    description="Package service",
    factory=repository_root_factory
)
package_version = Service(
    name="package_by_version",
    path="/api/package/{package_name}/{version}/json",
    description="Package service",
    factory=repository_root_factory
)


@package.get()
def get_package(request):
    package_name = request.matchdict.get('package_name')
    if package_name:
        package = request.context[package_name]
        if package:
            return PackageSerializer().serialize(package)
        else:
            return HTTPNotFound()


@packages.get()
def list_packages(request):
    serializer = PackageListSerializer()
    return [serializer.serialize(package) for package in request.context.values()]


@package_version.get()
def get_package_by_version(request):
    package_name = request.matchdict.get('package_name')
    version = request.matchdict.get('version')
    if package_name in request.context and version in request.context[package_name].releases.keys():
        serializer = ReleaseSerializer()
        return serializer.serialize(request.context[package_name][version])
    else:
        return HTTPNotFound()
