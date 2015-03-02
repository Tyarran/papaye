from pyramid.httpexceptions import HTTPNotFound
from cornice import Service

from papaye.serializers import PackageListSerializer, ReleaseAPISerializer
from papaye.factories import repository_root_factory
from papaye.models import Package, Release

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
            release = package.get_last_release()
            return ReleaseAPISerializer(request).serialize(release)
        else:
            return HTTPNotFound()


@package.delete()
def remove_package(request):
    package_name = request.matchdict.get('package_name')
    package = Package.by_name(package_name, request)
    if package is None:
        return HTTPNotFound()
    del request.root[package_name]
    return {'success': True}


@package.delete()
def remove_release(request):
    package_name = request.matchdict.get('package_name')
    version = request.matchdict.get('release_name')
    release = Release.by_releasename(package_name, version, request)
    if release is None:
        return HTTPNotFound()
    del request.root[package_name][version]
    return {'success': True}


@packages.get()
def list_packages(request):
    serializer = PackageListSerializer()
    packages = [serializer.serialize(package) for package in request.context.values()]
    return {
        'count': len(packages),
        'result': packages,
    }


@package_version.get()
def get_package_by_version(request):
    package_name = request.matchdict.get('package_name')
    version = request.matchdict.get('version')
    if package_name in request.context and version in request.context[package_name].releases.keys():
        serializer = ReleaseAPISerializer(request=request)
        return serializer.serialize(request.context[package_name][version])
    else:
        return HTTPNotFound()
