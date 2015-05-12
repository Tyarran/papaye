import io
import json
import types
import unittest

from cgi import FieldStorage
from mock import patch
from pyramid import testing
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.threadlocal import get_current_registry
from requests.exceptions import ConnectionError

from papaye.tests.tools import (
    disable_cache,
    FakeGRequestResponse,
    FakeRoute,
    mock_proxy_response,
    remove_blob_dir,
    set_database_connection,
)


class ListPackageViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.blob_dir = set_database_connection(self.request)
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple*traverse', factory='papaye.factories:repository_root_factory')
        registry = get_current_registry()
        registry.settings = disable_cache()

    def tearDown(self):
        remove_blob_dir(self.blob_dir)

    def test_list_packages(self):
        from papaye.views.simple import ListPackagesView
        from papaye.models import Package, Root

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')

        view = ListPackagesView(root, self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([package.name for url, package in response['objects']], ['package1', 'package2'])

    def test_list_packages_without_package(self):
        from papaye.views.simple import ListPackagesView
        from papaye.models import Root  # Test packages
        root = Root()

        view = ListPackagesView(root, self.request)
        response = view()
        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([package.name for url, package in response['objects']], [])


class ListReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.blob_dir = set_database_connection(self.request)
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple*traverse', factory='papaye.factories:repository_root_factory')
        registry = get_current_registry()
        registry.settings = disable_cache()

    def tearDown(self):
        remove_blob_dir(self.blob_dir)

    def test_list_releases_files(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0', metadata={})
        root['package1']['release1'].__parent__ = root['package1']
        root['package1']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile1.tar.gz'].__parent__ = root['package1']['release1']

        view = ListReleaseFileView(root['package1'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
              root['package1']['release1']['releasefile1.tar.gz'].__name__)]
        )

    def test_list_releases_files_with_multiple_files(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0', metadata={})
        root['package1']['release1'].__parent__ = root['package1']
        root['package1']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile1.tar.gz'].__parent__ = root['package1']['release1']
        root['package1']['release1']['releasefile2.tar.gz'] = ReleaseFile(filename='releasefile2.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile2.tar.gz'].__parent__ = root['package1']['release1']

        view = ListReleaseFileView(root['package1'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile1.tar.gz'].__name__),
                ('http://example.com/simple/package1/release1/releasefile2.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile2.tar.gz'].__name__),
            ],
        )

    def test_list_releases_files_with_multiple_release(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0', metadata={})
        root['package1']['release1'].__parent__ = root['package1']
        root['package1']['release2'] = Release(name='release2', version='2.0', metadata={})
        root['package1']['release2'].__parent__ = root['package1']
        root['package1']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile1.tar.gz'].__parent__ = root['package1']['release1']
        root['package1']['release2']['releasefile2.tar.gz'] = ReleaseFile(filename='releasefile2.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release2']['releasefile2.tar.gz'].__parent__ = root['package1']['release2']

        view = ListReleaseFileView(root['package1'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile1.tar.gz'].__name__),
                ('http://example.com/simple/package1/release2/releasefile2.tar.gz#md5=12345',
                 root['package1']['release2']['releasefile2.tar.gz'].__name__),
            ],
        )

    def test_list_releases_files_with_another_package(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['release1'] = Release(name='release1', version='1.0', metadata={})
        root['package1']['release1'].__parent__ = root['package1']
        root['package2']['release2'] = Release(name='release2', version='2.0', metadata={})
        root['package2']['release2'].__parent__ = root['package2']
        root['package1']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile1.tar.gz'].__parent__ = root['package1']['release1']
        root['package2']['release2']['releasefile2.tar.gz'] = ReleaseFile(filename='releasefile2.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package2']['release2']['releasefile2.tar.gz'].__parent__ = root['package2']['release2']

        view = ListReleaseFileView(root['package1'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile1.tar.gz'].__name__),
            ],
        )

        view = ListReleaseFileView(root['package2'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release.__name__) for url, release in response['objects']],
            [
                ('http://example.com/simple/package2/release2/releasefile2.tar.gz#md5=12345',
                 root['package2']['release2']['releasefile2.tar.gz'].__name__),
            ],
        )

    @patch('requests.get')
    @patch('papaye.models.Package.get_last_remote_version')
    def test_list_releases_files_with_new_remotes_release(self, mock, requests_mock):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        mock.return_value = "3.0"

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0', metadata={})
        root['package1']['release1'].__parent__ = root['package1']
        root['package1']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile1.tar.gz'].__parent__ = root['package1']['release1']

        self.request.matchdict['traverse'] = (root['package1'].__name__, root['package1']['release1'].__name__)
        self.request.registry.settings['papaye.proxy'] = 'true'
        view = ListReleaseFileView(root['package1'], self.request)
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
        root = Root()
        root['pyramid'] = Package(name='pyramid')
        root['pyramid']['release1'] = Release(name='release1', version='1.0', metadata={})
        root['pyramid']['release1'].__parent__ = root['pyramid']
        root['pyramid']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                         content=b'',
                                                                         md5_digest='12345')
        root['pyramid']['release1']['releasefile1.tar.gz'].__parent__ = root['pyramid']['release1']

        self.request.matchdict['traverse'] = (root['pyramid'].__name__, root['pyramid']['release1'].__name__)
        self.request.registry.settings['papaye.proxy'] = 'true'
        view = ListReleaseFileView(root['pyramid'], self.request)

        response = view()

        self.assertIsInstance(response, dict)
        assert len(list(response['objects'])) == 82


class DownloadReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.blob_dir = set_database_connection(self.request)
        settings = disable_cache()
        self.config = testing.setUp(request=self.request, settings=settings)
        self.config.add_route('simple', '/simple*traverse', factory='papaye.factories:repository_root_factory')

    def tearDown(self):
        remove_blob_dir(self.blob_dir)

    @patch('requests.get')
    def test_download_release(self, mock):
        from papaye.views.simple import DownloadReleaseView
        from papaye.models import ReleaseFile, Release, Package

        package = Package(name='package')
        release = Release(name='1.0', version='1.0', metadata={})
        release_file = ReleaseFile(filename='releasefile-1.0.tar.gz', content=b'Hello')
        release_file.content_type = 'text/plain'
        package['1.0'] = release
        package['1.0']['releasefile-1.0.tar.gz'] = release_file

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

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body, b'Hello')
        self.assertEqual(result.content_type, 'text/plain')
        self.assertEqual(result.content_disposition, 'attachment; filename="releasefile-1.0.tar.gz"')


class UploadReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)

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
        root = Root()
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
        root = Root()

        # Create initial release
        package = Package('my_package')
        package['1.0'] = Release('1.0', '1.0', metadata={})
        package['1.0']['foo.tar.gz'] = ReleaseFile('foo.tar.gz', b'')
        root['my-package'] = package

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
        root = Root()

        # Create initial release
        package = Package('my-package')
        package['1.0'] = Release('1.0', '1.0', metadata={})
        package['1.0']['foo.tar.gz'] = ReleaseFile('foo.tar.gz', b'Fake Content')
        root['my-package'] = package

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
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.blob_dir = set_database_connection(self.request)
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple*traverse', factory='papaye.factories:repository_root_factory')
        registry = get_current_registry()
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
        }

    def tearDown(self):
        remove_blob_dir(self.blob_dir)

    def test_list_release(self):
        from papaye.views.simple import ListReleaseFileByReleaseView
        from papaye.models import Package, Release, ReleaseFile
        from papaye.factories import repository_root_factory

        # Initial data
        root = repository_root_factory(self.request)
        package = Package('my_package')
        package['1.0'] = Release('1.0', '1.0', metadata={})
        package['1.0']['foo.tar.gz'] = ReleaseFile('foo.tar.gz', b'')
        root['my_package'] = package
        view = ListReleaseFileByReleaseView(package['1.0'], self.request)

        result = view()

        self.assertIsInstance(result, dict)
        self.assertIn('objects', result)
        self.assertEqual(list(result['objects']), [('http://example.com/simple/my_package/1.0/foo.tar.gz/',
                                                    package['1.0']['foo.tar.gz'])])

    def test_list_release_with_two_release(self):
        from papaye.views.simple import ListReleaseFileByReleaseView
        from papaye.models import Package, Release, ReleaseFile
        from papaye.factories import repository_root_factory

        # Initial data
        root = repository_root_factory(self.request)
        package = Package('my_package')
        package['1.0'] = Release('1.0', '1.0', metadata={})
        package['1.0']['foo.tar.gz'] = ReleaseFile('foo.tar.gz', b'')
        package['2.0'] = Release('2.0', '2.0', metadata={})
        package['2.0']['foo2.tar.gz'] = ReleaseFile('foo2.tar.gz', b'')
        root['my_package'] = package
        view1 = ListReleaseFileByReleaseView(package['1.0'], self.request)
        view2 = ListReleaseFileByReleaseView(package['2.0'], self.request)

        result1 = view1()
        result2 = view2()

        self.assertIsInstance(result1, dict)
        self.assertIn('objects', result1)
        self.assertEqual(list(result1['objects']), [('http://example.com/simple/my_package/1.0/foo.tar.gz/',
                                                     package['1.0']['foo.tar.gz'])])
        self.assertIsInstance(result2, dict)
        self.assertIn('objects', result2)
        self.assertEqual(list(result2['objects']), [('http://example.com/simple/my_package/2.0/foo2.tar.gz/',
                                                     package['2.0']['foo2.tar.gz'])])

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
        root = Root()
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
    from papaye.views.index import login_view
    config = testing.setUp()
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)
    request = testing.DummyRequest()
    request.POST = {'login': 'user', 'password': 'seekrit'}
    request.root = Root()
    request.root['user'] = User('user', 'seekrit')

    result = login_view(request)

    assert isinstance(result, Response) is True
    assert 'Set-Cookie' in result.headers
    assert 'username' in request.session
    assert request.session['username'] == 'user'


def test_login_view_bad_password():
    from papaye.models import User, Root
    from papaye.views.index import login_view
    config = testing.setUp()
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)
    request = testing.DummyRequest()
    request.POST = {'login': 'user', 'password': 'seekrit'}
    request.root = Root()
    request.root['user'] = User('user', 'bad password')

    result = login_view(request)

    assert isinstance(result, Response) is True
    assert result.status_code == 401
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
    assert mock.call_count == 2
