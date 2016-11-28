import pytest

from pyramid.httpexceptions import HTTPNotFound
from pyramid import testing

from papaye.tests.tools import set_database_connection

@pytest.fixture(autouse=True)
def repo_config(request):
    settings = {
        'papaye.proxy': False,
        'pyramid.incluces': 'pyramid_zodbconn',
    }
    req = testing.DummyRequest()
    set_database_connection(req)
    config = testing.setUp(settings=settings, request=req)
    config.add_route(
        'simple',
        '/simple/*traverse',
        factory='papaye.factories:repository_root_factory'
    )


def test_get_packages(request_factory):
    from papaye.views.api import list_packages
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package2'] = Package(name='package2')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1',
        'description': 'A description',
    })
    root['package2']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 2',
        'description': 'A description',
    })
    expected = [{
        'name': 'package1',
        'summary': 'The package 1',
    }, {
        'name': 'package2',
        'summary': 'The package 2',
    }, ]
    request.context = root

    result = list_packages(request)

    assert isinstance(result, dict) is True
    assert 'result' in result
    assert isinstance(result['result'], list) is True
    assert 'count' in result
    assert result['count'] == 2
    assert len(result['result']) == 2
    assert isinstance(result['result'][0], dict) is True
    assert [dict(element) for element in result['result']] == expected


def test_get_packages_with_no_package_in_database(request_factory):
    from papaye.views.api import list_packages
    from papaye.models import Root
    request = request_factory(settings={})
    root = Root()
    request.context = root

    result = list_packages(request)

    assert isinstance(result, dict) is True
    assert 'result' in result
    assert isinstance(result['result'], list) is True
    assert 'count' in result
    assert result['count'] == 0
    assert len(result['result']) == 0
    assert result['result'] == []


def test_get_package(request_factory):
    from papaye.views.api import get_package
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package2'] = Package(name='package2')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1',
        'description': 'A description',
    })
    root['package2']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 2',
        'description': 'A description',
    })
    request.context = root
    request.matchdict = {'package_name': 'package1'}

    result = get_package(request)

    assert isinstance(result, dict) is True
    assert result['name'] == 'package1'
    assert 'metadata' in result


def test_get_package_unknown(request_factory):
    from papaye.views.api import get_package
    from papaye.models import Root
    request = request_factory(settings={})
    root = Root()
    request.context = root
    request.matchdict = {'package_name': 'package1'}

    result = get_package(request)

    assert isinstance(result, HTTPNotFound) is True


def test_get_package_by_version(request_factory, config_factory):
    from papaye.views.api import get_package_by_version
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    config = config_factory(
        settings={},
        request=request
    )
    config.add_route(
        'simple',
        '/simple/*traverse',
        factory='papaye.factories:repository_root_factory'
    )
    root = Root()
    root['package1'] = Package(name='package1')
    root['package2'] = Package(name='package2')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1',
        'description': 'A description',
    })
    root['package2']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 2',
        'description': ''
    })
    request.context = root
    request.matchdict = {'package_name': 'package1', 'version': '1.0'}

    result = get_package_by_version(request)

    assert isinstance(result, dict) is True


def test_get_package_by_version_with_unknown_package(request_factory,
                                                     config_factory):
    from papaye.views.api import get_package_by_version
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    config = config_factory(request=request)
    config.add_route('simple', '/simple/*traverse',
                     factory='papaye.factories:repository_root_factory')
    root = Root()
    root = Root()
    root['package1'] = Package(name='package1')
    root['package2'] = Package(name='package2')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1'
    })
    root['package2']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 2'
    })
    request.context = root
    request.matchdict = {'package_name': 'package3', 'version': '1.0'}

    result = get_package_by_version(request)

    assert isinstance(result, HTTPNotFound) is True


def test_get_package_by_version_with_unknown_release(request_factory):
    from papaye.views.api import get_package_by_version
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package2'] = Package(name='package2')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1'
    })
    root['package2']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 2'
    })
    request.context = root
    request.matchdict = {'package_name': 'package2', 'version': '2.0'}

    result = get_package_by_version(request)

    assert isinstance(result, HTTPNotFound) is True


def test_remove_package(request_factory):
    from papaye.views.api import remove_package
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1'
    })
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1'}

    result = remove_package(request)

    assert isinstance(result, dict)
    assert 'success' in result
    assert result['success']
    assert 'package1' not in root


def test_remove_package_not_existing(request_factory):
    from papaye.views.api import remove_package
    from papaye.models import Root
    request = request_factory(settings={})
    root = Root()
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1'}

    result = remove_package(request)

    assert isinstance(result, HTTPNotFound)


def test_remove_release(request_factory):
    from papaye.views.api import remove_release
    from papaye.models import Package, Root, Release
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1',
        'description': 'A description',
    })
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1', 'version': '1.0'}

    result = remove_release(request)

    assert isinstance(result, dict)
    assert 'success' in result
    assert result['success']
    assert 'package1' in [pkg.__name__ for pkg in root]
    assert '1.0' not in [rel.__name__ for rel in root['package1']]


def test_remove_release_not_existing_package(request_factory):
    from papaye.views.api import remove_release
    from papaye.models import Root
    request = request_factory(settings={})
    root = Root()
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1', 'version': '1.0'}

    result = remove_release(request)

    assert isinstance(result, HTTPNotFound)


def test_remove_release_not_existing_release(request_factory):
    from papaye.views.api import remove_release
    from papaye.models import Root, Package
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1', 'version': '1.0'}

    result = remove_release(request)

    assert isinstance(result, HTTPNotFound)


def rest_remove_releasefile(request_factory):
    from papaye.views.api import remove_releasefile
    from papaye.models import Package, Root, Release, ReleaseFile
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1',
        'description': 'A description',
    })
    root['package1']['1.0']['package1-1.0.tar.gz'] = ReleaseFile(
        'package1-1.0.tar.gz', b''
    )
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1', 'version': '1.0',
                         'filename': 'package1-1.0.tar.gz'}

    result = remove_releasefile(request)

    assert isinstance(result, dict)
    assert 'success' in result
    assert result['success']
    assert 'package1' in [pkg.__name__ for pkg in root]
    assert len(list(root['package1'])) == 1
    assert len(list(root['package1']['1.0'])) == 0


def test_remove_releasefile_not_existing_package(request_factory):
    from papaye.views.api import remove_releasefile
    from papaye.models import Root
    request = request_factory(settings={})
    root = Root()
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1',
                         'version': '1.0',
                         'filename': 'package1-1.0.tar.gz'}

    result = remove_releasefile(request)

    assert isinstance(result, HTTPNotFound)


def test_remove_releasefile_not_existing_release(request_factory):
    from papaye.views.api import remove_releasefile
    from papaye.models import Root, Package
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1',
                         'version': '1.0',
                         'filename': 'package1-1.0.tar.gz'}

    result = remove_releasefile(request)

    assert isinstance(result, HTTPNotFound)


def test_remove_releasefile_not_existing_releasefile(request_factory):
    from papaye.views.api import remove_releasefile
    from papaye.models import Root, Package, Release
    request = request_factory(settings={})
    root = Root()
    root['package1'] = Package(name='package1')
    root['package1']['1.0'] = Release('1.0', '1.0', {
        'summary': 'The package 1',
        'description': 'A description',
    })
    request.context = root
    request.root = root
    request.matchdict = {'package_name': 'package1',
                         'version': '1.0',
                         'filename': 'package1-1.0.tar.gz'}

    result = remove_releasefile(request)

    assert isinstance(result, HTTPNotFound)
