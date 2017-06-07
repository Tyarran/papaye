import os
import pytest
import shutil
import tempfile

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from pyramid.threadlocal import get_current_request

from papaye.tests.tools import set_database_connection
from papaye.factories import models as factories


@pytest.fixture(autouse=True)
def repo_config(request):
    tmpdir = tempfile.mkdtemp('test_repo')
    settings = {
        'papaye.proxy': False,
        'papaye.packages_directory': tmpdir,
        'pyramid.incluces': 'pyramid_zodbconn',
    }
    req = testing.DummyRequest()
    set_database_connection(req)
    config = testing.setUp(settings=settings, request=req)
    config.add_route(
        'simple',
        '/simple/*traverse',
        factory='papaye.factories.root:repository_root_factory'
    )
    config.add_static_view(
        'repo',
        tmpdir,
        cache_max_age=3600,
    )

    def clean_tmp_dir():
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    request.addfinalizer(clean_tmp_dir)


def create_repository(nb_release_file):
    root = factories.RootFactory()
    packages = []
    for index in range(1, nb_release_file + 1):
        release_file = factories.ReleaseFileFactory(
            release__metadata={
                'summary': 'The package {}'.format(index),
                'description': 'A description',
            },
            release__version='1.0',
            release__package__root=root,
        )
        packages.append(release_file.release.package)
    return root, packages


def test_get_packages(request_factory):
    from papaye.views.api.compat.api import list_packages
    request = request_factory(settings={})
    root = factories.RootFactory()
    release1 = factories.ReleaseFactory(
        version='1.0',
        metadata={
            'summary': 'The package 1',
            'description': 'A description',
        },
        package__name='package1',
        package__root=root,
    )
    release2 = factories.ReleaseFactory(
        version='1.0',
        metadata={
            'summary': 'The package 2',
            'description': 'A description',
        },
        package__name='package2',
        package__root=root,
    )
    expected = [
        release1.package,
        release2.package,
    ]
    request.context = root

    result = list_packages(request)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result == expected


def test_get_packages_without_package_in_database(request_factory):
    from papaye.views.api.compat.api import list_packages
    request = request_factory(settings={})
    root = factories.RootFactory()
    request.context = root

    result = list_packages(request)

    assert isinstance(result, list)
    assert result == []


def test_get_package(repo_config):
    from papaye.views.api.compat.api import get_package
    from papaye.models import Release
    request = get_current_request()
    root, packages = create_repository(2)
    request.context = packages[0]

    result = get_package(request)

    assert isinstance(result, Release)
    assert result.package.name == packages[0].name


def test_get_package_by_version():
    from papaye.views.api.compat.api import get_package_by_version
    from papaye.models import Release
    request = get_current_request()
    root, packages = create_repository(2)
    request.context = root
    request.validated = {
        'path': {
            'package_name': packages[0].name,
            'version': packages[0]['1.0'].version,
        }
    }

    result = get_package_by_version(request)

    assert isinstance(result, Release)


def test_get_package_by_version_with_unknown_package(request_factory,
                                                     config_factory):
    from papaye.views.api.compat.api import get_package_by_version
    request = get_current_request()
    root, packages = create_repository(2)
    request.context = root
    request.validated = {
        'path': {
            'package_name': 'package'.format(len(packages) + 1),
            'version': '1.0'
        }
    }

    result = get_package_by_version(request)

    assert isinstance(result, HTTPNotFound)


def test_get_package_by_version_with_unknown_release(request_factory):
    from papaye.views.api.compat.api import get_package_by_version
    request = request_factory(settings={})
    root, packages = create_repository(2)
    request.context = root
    request.validated = {
        'path': {'package_name': packages[0].name, 'version': '2.0'}
    }

    result = get_package_by_version(request)

    assert isinstance(result, HTTPNotFound)