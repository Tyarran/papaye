import io
import json
import types
import unittest

from cgi import FieldStorage
from mock import patch
from pyramid import testing
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.threadlocal import get_current_request
from requests.exceptions import ConnectionError

from papaye.tests.tools import disable_cache, FakeGRequestResponse
from papaye.tests.tools import mock_proxy_response
from papaye.factories import models as factories


class ListPackageViewTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()

    def test_list_packages(self):
        from papaye.views.simple import ListPackagesView

        # Test packages
        root = factories.RootFactory()
        factories.PackageFactory(name='package1', root=root)
        factories.PackageFactory(name='package2', root=root)

        view = ListPackagesView(root, self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([
            package.name for url,
            package in response['objects']
        ], ['package1', 'package2'])

    def test_list_packages_without_package(self):
        from papaye.views.simple import ListPackagesView
        root = factories.RootFactory()

        view = ListPackagesView(root, self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([package.name for url, package in response['objects']], [])


class ListReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()

    def test_list_releases_files(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = factories.RootFactory()
        package = factories.PackageFactory(name='package1', root=root)
        release = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package
        )
        factories.ReleaseFileFactory(
            filename='releasefile1.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release,
        )

        view = ListReleaseFileView(root['package1'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [('http://example.com/simple/package1/1.0/releasefile1.tar.gz#md5=12345',
              root['package1']['1.0']['releasefile1.tar.gz'].__name__)]
        )

    def test_list_releases_files_with_multiple_files(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, ReleaseFile

        # Test packages
        root = factories.RootFactory()
        package1 = factories.PackageFactory(name='package1', root=root)
        release = factories.ReleaseFactory(
            version='1.0', package=package1
        )
        release_file1 = factories.ReleaseFileFactory(
            filename='releasefile1.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release,
        )
        release_file2 = factories.ReleaseFileFactory(
            filename='releasefile2.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release,
        )

        view = ListReleaseFileView(root['package1'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/1.0/'
                 'releasefile1.tar.gz#md5=12345',
                 release_file1.filename),
                ('http://example.com/simple/package1/1.0/'
                 'releasefile2.tar.gz#md5=12345',
                 release_file2.filename),
            ],
        )

    def test_list_releases_files_with_multiple_release(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = factories.RootFactory()
        package = factories.PackageFactory(name='package1', root=root)
        release1 = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package,
        )
        release2 = factories.ReleaseFactory(
            version='2.0', metadata={}, package=package,
        )
        factories.ReleaseFileFactory(
            filename='releasefile1.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release1,
        )
        factories.ReleaseFileFactory(
            filename='releasefile2.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release2,
        )

        view = ListReleaseFileView(package, self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/1.0/releasefile1.tar.gz#md5=12345',
                 root['package1']['1.0']['releasefile1.tar.gz'].__name__),
                ('http://example.com/simple/package1/2.0/releasefile2.tar.gz#md5=12345',
                 root['package1']['2.0']['releasefile2.tar.gz'].__name__),
            ],
        )

    def test_list_releases_files_with_another_package(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = factories.RootFactory()
        package1 = factories.PackageFactory(name='package1', root=root)
        package2 = factories.PackageFactory(name='package2', root=root)
        release1 = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package1,
        )
        release2 = factories.ReleaseFactory(
            version='2.0', metadata={}, package=package2,
        )
        factories.ReleaseFileFactory(
            filename='releasefile1.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release1,
        )
        factories.ReleaseFileFactory(
            filename='releasefile2.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release2,
        )

        view = ListReleaseFileView(root['package1'], self.request)
        view.stop = True

        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.filename) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/1.0/releasefile1.tar.gz#md5=12345',
                 root['package1']['1.0']['releasefile1.tar.gz'].filename),
            ],
        )

        view = ListReleaseFileView(root['package2'], self.request)
        view.stop = True
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.filename) for url, release in response['objects']],
            [
                ('http://example.com/simple/package2/2.0/releasefile2.tar.gz#md5=12345',
                 root['package2']['2.0']['releasefile2.tar.gz'].filename),
            ],
        )

    @patch('requests.get')
    @patch('papaye.models.Package.get_last_remote_version')
    def test_list_releases_files_with_new_remotes_release(self, mock, requests_mock):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        mock.return_value = "3.0"

        # Test packages
        root = factories.RootFactory()
        package = factories.PackageFactory(name='package1', root=root)
        release = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package,
        )
        factories.ReleaseFileFactory(
            filename='releasefile1.tar.gz',
            content=b'',
            md5_digest='12345',
            release=release,
        )

        self.request.matchdict['traverse'] = (package.name, release.name)
        self.request.registry.settings['papaye.proxy'] = 'true'
        view = ListReleaseFileView(package, self.request)
        pypi_result = {
            'info': {
                'name': 'package1',
            },
            'releases': {
                'release1': [{
                    'filename': 'releasefile1.tar.gz',
                    'url': 'http://example.com/',
                    'md5_digest': 'fake md5',
                }]
            }
        }
        requests_mock.return_value = FakeGRequestResponse(200, bytes(json.dumps(pypi_result), 'utf-8'))
        response = view()

        self.assertIsInstance(response, dict)

    @patch('requests.get')
    def test_list_releases_with_proxy(self, mock):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        mock_proxy_response(mock)

        # Test packages
        root = factories.RootFactory()
        package = factories.PackageFactory(name='pyramid', root=root)
        release = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package
        )
        release_file = factories.ReleaseFileFactory(
            filename='releasefile1.tar.gz', content=b'',
            md5_digest='12345',
            release=release,
        )

        self.request.matchdict['traverse'] = (package.name, release.version)
        self.request.registry.settings['papaye.proxy'] = 'true'
        view = ListReleaseFileView(package, self.request)

        response = view()

        self.assertIsInstance(response, dict)
        assert len(list(response['objects'])) == 82


class DownloadReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()

    @patch('requests.get')
    def test_download_release(self, mock):
        from papaye.views.simple import DownloadReleaseView
        from papaye.models import ReleaseFile, Release, Package

        package = factories.PackageFactory(name='package')
        release = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package,
        )
        release_file = factories.ReleaseFileFactory(
            filename='releasefile-1.0.tar.gz',
            content=b'Hello',
            release=release,
        )
        release_file.content_type = 'text/plain'

        pypi_response = {
            'info': {
                'name': 'package',
                'version': '1.0'
            },
            'releases': {
                '1.0': [{
                    'filename': 'releasefile1.tar.gz',
                    'url': 'http://example.com/',
                    'md5_digest': 'fake md5',
                }]
            }
        }
        mock.return_value = FakeGRequestResponse(200, bytes(json.dumps(pypi_response), 'utf-8'))

        self.request.registry.settings['papaye.proxy'] = 'true'
        view = DownloadReleaseView(release_file, self.request)
        result = view()

        self.assertEqual(result.status_code, 307)


class UploadReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()

    def test_upload_release(self):
        from papaye.models import Root, Package, Release, ReleaseFile, STATUS
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO(b"content")
        storage = FieldStorage()
        storage.filename = 'foo.tar.gz'
        storage.file = uploaded_file

        self.request.POST = {
            "content": storage,
            "some_metadata": "Fake Metadata",
            "version": "1.0",
            "name": "my_package",
            ":action": "file_upload",
            "md5_digest": "Fake MD5"
        }
        root = factories.RootFactory()
        self.request.root = root
        view = UploadView(root, self.request)
        result = view()

        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 200)
        self.assertTrue('my-package' in root)
        self.assertIsInstance(root['my-package'], Package)
        self.assertTrue(root['my-package'].releases.get('1.0', False))
        self.assertIsInstance(root['my-package']['1.0'], Release)
        self.assertTrue(root['my-package']['1.0'].release_files.get('foo.tar.gz', b''))
        self.assertIsInstance(root['my-package']['1.0']['foo.tar.gz'], ReleaseFile)
        self.assertEqual(root['my-package']['1.0']['foo.tar.gz'].md5_digest, "Fake MD5")
        self.assertIsNotNone(root['my-package']['1.0'].metadata)
        self.assertIsInstance(root['my-package']['1.0'].metadata, dict)
        self.assertEqual(root['my-package']['1.0'].release_files.get('foo.tar.gz', b'').size, 7)
        assert root['my-package']['1.0']['foo.tar.gz'].status == STATUS.local

    def test_upload_release_already_exists(self):
        from papaye.models import Root, Package, Release, ReleaseFile
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO(b"content")
        storage = FieldStorage()
        storage.filename = 'foo.tar.gz'
        storage.file = uploaded_file

        self.request.POST = {
            "content": storage,
            "some_metadata": "Fake Metadata",
            "version": "1.0",
            "name": "my_package",
            ":action": "file_upload",
        }
        root = factories.RootFactory()

        # Create initial release
        package = factories.PackageFactory(name='my_package', root=root)
        release = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package,
        )
        factories.ReleaseFileFactory(
            filename='foo.tar.gz',
            content=b'',
            release=release,
        )

        view = UploadView(root, self.request)
        result = view()

        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 409)

    def test_upload_release_multiple_releasefile(self):
        from papaye.models import Root, Package, Release, ReleaseFile
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO(b"content")
        storage = FieldStorage()
        storage.filename = 'foo.zip'
        storage.file = uploaded_file

        self.request.POST = {
            "content": storage,
            "some_metadata": "Fake Metadata",
            "version": "1.0",
            "name": "my_package",
            ":action": "file_upload",
        }
        root = factories.RootFactory()

        # Create initial release
        package = factories.PackageFactory(name='my-package', root=root)
        release = factories.ReleaseFactory(
            version='1.0', metadata={}, package=package,
        )
        factories.ReleaseFileFactory(
            filename='foo.tar.gz', content=b'Fake Content', release=release,
        )

        view = UploadView(root, self.request)
        result = view()

        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 200)
        self.assertTrue('my-package' in root)
        self.assertIsInstance(root['my-package'], Package)
        self.assertTrue(root['my-package'].releases.get('1.0', False))
        self.assertIsInstance(root['my-package']['1.0'], Release)
        self.assertTrue(root['my-package']['1.0'].release_files.get('foo.tar.gz', b''))
        self.assertIsInstance(root['my-package']['1.0']['foo.tar.gz'], ReleaseFile)
        self.assertTrue(root['my-package']['1.0'].release_files.get('foo.zip', b''))
        self.assertIsInstance(root['my-package']['1.0']['foo.zip'], ReleaseFile)
        self.assertEqual(root['my-package']['1.0'].release_files.get('foo.tar.gz', b'').size, 12)


class ListReleaseFileByReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()

    def test_list_release(self):
        from papaye.views.simple import ListReleaseFileByReleaseView
        from papaye.models import Package, Release, ReleaseFile
        from papaye.factories.root import repository_root_factory

        # Initial data
        root = repository_root_factory(self.request)
        package = factories.PackageFactory(name='my_package', root=root)
        release = factories.ReleaseFactory(version='1.0', metadata={}, package=package)
        release_file = factories.ReleaseFileFactory(
            filename='foo.tar.gz', release=release
        )
        view = ListReleaseFileByReleaseView(release, self.request)

        result = view()

        self.assertIsInstance(result, dict)
        self.assertIn('objects', result)
        self.assertEqual(list(result['objects']), [('http://example.com/simple/my_package/1.0/foo.tar.gz/',
                                                    release_file)])

    def test_list_release_with_two_release(self):
        from papaye.views.simple import ListReleaseFileByReleaseView
        from papaye.models import Package, Release, ReleaseFile
        from papaye.factories.root import repository_root_factory

        # Initial data
        root = repository_root_factory(self.request)

        package = factories.PackageFactory(name='my_package', root=root)
        release = factories.ReleaseFactory(version='1.0', metadata={}, package=package)
        release2 = factories.ReleaseFactory(
            version='2.0', metadata={}, package=package,
        )
        release_file = factories.ReleaseFileFactory(
            filename='foo.tar.gz', release=release,
        )
        release_file2 = factories.ReleaseFileFactory(
            filename='foo2.tar.gz', release=release2,
        )

        view1 = ListReleaseFileByReleaseView(release, self.request)
        view2 = ListReleaseFileByReleaseView(release2, self.request)

        result1 = view1()
        result2 = view2()

        self.assertIsInstance(result1, dict)
        self.assertIn('objects', result1)
        self.assertEqual(list(result1['objects']), [('http://example.com/simple/my_package/1.0/foo.tar.gz/',
                                                     release_file)])
        self.assertIsInstance(result2, dict)
        self.assertIn('objects', result2)
        self.assertEqual(list(result2['objects']), [('http://example.com/simple/my_package/2.0/foo2.tar.gz/',
                                                     release_file2)])

    def test_upload_release_with_spaces(self):
        from papaye.models import Root, Package, Release, ReleaseFile
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO(b"content")
        storage = FieldStorage()
        storage.filename = 'foo.tar.gz'
        storage.file = uploaded_file

        self.request.POST = {
            "content": storage,
            "some_metadata": "Fake Metadata",
            "version": "1.0",
            "name": "my package",
            ":action": "file_upload",
            "md5_digest": "Fake MD5"
        }
        root = factories.RootFactory()
        self.request.root = root
        view = UploadView(root, self.request)
        result = view()

        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 200)
        self.assertTrue('my-package' in root)
        self.assertIsInstance(root['my-package'], Package)
        self.assertTrue(root['my-package'].releases.get('1.0', False))
        self.assertIsInstance(root['my-package']['1.0'], Release)
        self.assertTrue(root['my-package']['1.0'].release_files.get('foo.tar.gz', b''))
        self.assertIsInstance(root['my-package']['1.0']['foo.tar.gz'], ReleaseFile)
        self.assertEqual(root['my-package']['1.0']['foo.tar.gz'].md5_digest, "Fake MD5")
        self.assertIsNotNone(root['my-package']['1.0'].metadata)
        self.assertIsInstance(root['my-package']['1.0'].metadata, dict)
        self.assertEqual(root['my-package']['1.0'].release_files.get('foo.tar.gz', b'').size, 7)


def test_login_view():
    from papaye.models import User, Root
    from papaye.views.index import LoginView
    config = testing.setUp()
    config.add_route('home', '/')
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)
    request = testing.DummyRequest()
    request.method = 'POST'
    request.POST = {'username': 'user', 'password': 'seekrit'}
    request.root = factories.RootFactory()
    request.root['user'] = User('user', 'seekrit')

    login_view = LoginView(request)
    result = login_view()

    assert isinstance(result, HTTPMovedPermanently)
    assert 'Set-Cookie' in result.headers
    assert 'username' in request.session
    assert request.session['username'] == 'user'


def test_login_view_bad_password():
    from papaye.models import User, Root
    from papaye.views.index import LoginView
    config = testing.setUp()
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)
    request = testing.DummyRequest()
    request.POST = {'username': 'user', 'password': 'seekrit'}
    request.root = factories.RootFactory()
    request.root['user'] = User('user', 'bad password')

    login_view = LoginView(request)
    result = login_view()

    assert isinstance(result, dict)
    assert 'username' not in request.session


@patch('requests.get')
def test_not_found_view_with_no_proxy(mock):
    from papaye.views.simple import not_found
    settings = {'papaye.proxy': 'false'}
    request = testing.DummyRequest()
    request.matchdict = {'traverse': ('package',)}
    testing.setUp(request=request, settings=settings)
    mock.side_effect = ConnectionError

    result = not_found(request)

    assert isinstance(result, HTTPNotFound)


@patch('requests.get')
def test_not_found_view_package_not_found(mock):
    from papaye.views.simple import not_found
    settings = {'papaye.proxy': 'true'}
    settings = disable_cache(settings)
    request = testing.DummyRequest()
    request.matchdict = {'traverse': ('package',)}
    request.root = {}
    testing.setUp(request=request, settings=settings)
    mock.side_effect = ConnectionError

    result = not_found(request)

    assert isinstance(result, HTTPNotFound)
    assert mock.call_count == 1


def test_parse_matchdict_with_package():
    from papaye.views.simple import parse_matchdict
    matchdict = {'traverse': ('one', )}

    result = parse_matchdict(matchdict)

    assert result == {'package': 'one',  'desired_entity': 'package'}


def test_parse_matchdict_with_release():
    from papaye.views.simple import parse_matchdict
    matchdict = {'traverse': ('one', 'two')}

    result = parse_matchdict(matchdict)

    assert result == {
        'package': 'one',
        'release': 'two',
        'desired_entity': 'release'
    }


def test_parse_matchdict_with_release_file():
    from papaye.views.simple import parse_matchdict
    matchdict = {'traverse': ('one', 'two', 'three')}

    result = parse_matchdict(matchdict)

    assert result == {
        'package': 'one',
        'release': 'two',
        'release_file': 'three',
        'desired_entity': 'release_file'
    }
