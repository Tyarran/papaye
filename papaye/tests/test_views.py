import io
import json
import types
import unittest

from cgi import FieldStorage
from mock import patch
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.response import Response
from pyramid.threadlocal import get_current_registry
from pyramid_beaker import set_cache_regions_from_settings

from papaye.tests.tools import (
    FakeGRequestResponse,
    FakeRoute
)


class ListPackageViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple/*traverse', factory='papaye.factories:repository_root_factory')
        registry = get_current_registry()
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'memory://',
        }

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
        from papaye.models import Root

        # Test packages
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
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple/*traverse', factory='papaye.factories:repository_root_factory')
        registry = get_current_registry()
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'memory://',
        }
        set_cache_regions_from_settings(registry.settings)

    def test_list_releases_files(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0')
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
            [(url, release) for url, release in response['objects']],
            [('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
              root['package1']['release1']['releasefile1.tar.gz'])]
        )

    def test_list_releases_files_with_multiple_files(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0')
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
            [(url, release) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile1.tar.gz']),
                ('http://example.com/simple/package1/release1/releasefile2.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile2.tar.gz']),
            ],
        )

    def test_list_releases_files_with_multiple_release(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package1']['release1'] = Release(name='release1', version='1.0')
        root['package1']['release1'].__parent__ = root['package1']
        root['package1']['release2'] = Release(name='release2', version='2.0')
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
            [(url, release) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile1.tar.gz']),
                ('http://example.com/simple/package1/release2/releasefile2.tar.gz#md5=12345',
                 root['package1']['release2']['releasefile2.tar.gz']),
            ],
        )

    def test_list_releases_files_with_another_package(self):
        from papaye.views.simple import ListReleaseFileView
        from papaye.models import Package, Release, Root, ReleaseFile

        # Test packages
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['release1'] = Release(name='release1', version='1.0')
        root['package1']['release1'].__parent__ = root['package1']
        root['package2']['release2'] = Release(name='release2', version='2.0')
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
            [(url, release) for url, release in response['objects']],
            [
                ('http://example.com/simple/package1/release1/releasefile1.tar.gz#md5=12345',
                 root['package1']['release1']['releasefile1.tar.gz']),
            ],
        )

        view = ListReleaseFileView(root['package2'], self.request)
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [(url, release) for url, release in response['objects']],
            [
                ('http://example.com/simple/package2/release2/releasefile2.tar.gz#md5=12345',
                 root['package2']['release2']['releasefile2.tar.gz']),
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
        root['package1']['release1'] = Release(name='release1', version='1.0')
        root['package1']['release1'].__parent__ = root['package1']
        root['package1']['release1']['releasefile1.tar.gz'] = ReleaseFile(filename='releasefile1.tar.gz',
                                                                          content=b'',
                                                                          md5_digest='12345')
        root['package1']['release1']['releasefile1.tar.gz'].__parent__ = root['package1']['release1']

        self.request.matchdict['traverse'] = (root['package1'].__name__, root['package1']['release1'].__name__)
        view = ListReleaseFileView(root['package1'], self.request)
        view.proxy = True
        pypi_result = {
            'urls': [{
                'filename': 'releasefile1.tar.gz',
                'url': 'http://example.com/'
            }]
        }
        requests_mock.return_value = FakeGRequestResponse(200, bytes(json.dumps(pypi_result), 'utf-8'))
        response = view()

        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual(
            [url for url, release in response['objects']], [
                'http://example.com/',
                'http://example.com/simple/package1/release1/releasefile1.tar.gz?check_update=false#md5=12345',
            ],
        )


class DownloadReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple/*traverse', factory='papaye.factories:repository_root_factory')
        registry = self.request.registry
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'memory://',
        }
        set_cache_regions_from_settings(registry.settings)

    def test_download_release(self):
        from papaye.views.simple import DownloadReleaseView
        from papaye.models import ReleaseFile, Release, Package

        package = Package(name='package')
        release = Release(name='1.0', version='1.0')
        release_file = ReleaseFile(filename='releasefile-1.0.tar.gz', content=b'Hello')
        release_file.content_type = 'text/plain'
        release_file.__parent__ = release
        release.__parent__ = package

        view = DownloadReleaseView(release_file, self.request)
        result = view()

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body, b'Hello')
        self.assertEqual(result.content_type, 'text/plain')
        self.assertEqual(result.content_disposition, 'attachment; filename="releasefile-1.0.tar.gz"')

    @patch('papaye.models.Package.get_last_remote_version')
    def test_download_release_with_old_release(self, mock):
        from papaye.views.simple import DownloadReleaseView
        from papaye.models import ReleaseFile, Release, Package

        mock.return_value = '2.0'

        package = Package(name='package')
        release = Release(name='1.0', version='1.0')
        release_file = ReleaseFile(filename='releasefile-1.0.tar.gz', content=b'Hello')
        release_file.__parent__ = release
        release.__parent__ = package

        self.request.matchdict['traverse'] = (package.__name__, release.__name__, release_file.__name__)
        self.request.traversed = (package.__name__, release.__name__)

        view = DownloadReleaseView(release_file, self.request)
        result = view()

        self.assertIsInstance(result, HTTPNotFound)


class PackageNotFoundViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)
        registry = self.request.registry
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'memory://',
        }
        set_cache_regions_from_settings(registry.settings)

    @patch('requests.get')
    def test_package_not_found(self, mock):
        from papaye.views.simple import PackageNotFoundView

        view = PackageNotFoundView(self.request, 'Package')
        view.proxy = True
        view.request.matchdict['traverse'] = ('unknowpackage',)

        result = view()
        self.assertEqual(mock.call_count, 1)
        self.assertIsInstance(result, HTTPNotFound)

    @patch('requests.get')
    def test_package_not_found_without_proxy(self, mock):
        from papaye.views.simple import PackageNotFoundView

        view = PackageNotFoundView(self.request, 'Package')
        view.proxy = False
        view.request.matchdict['traverse'] = ('unknowpackage',)

        result = view()
        self.assertEqual(mock.call_count, 0)
        self.assertIsInstance(result, HTTPNotFound)

    @patch('requests.get')
    def test_package_not_found_present_in_pypi(self, mock):
        from papaye.views.simple import PackageNotFoundView

        mock.return_value = FakeGRequestResponse(200, '')

        view = PackageNotFoundView(self.request, 'Package')
        view.proxy = True
        view.request.matchdict['traverse'] = ('unknowpackage',)

        result = view()
        self.assertEqual(mock.call_count, 1)
        self.assertIsInstance(result, HTTPTemporaryRedirect)
        self.assertEqual(result.location, 'http://pypi.python.org/simple/unknowpackage/')

    @patch('requests.get')
    def test_package_not_found_not_present_in_pypi(self, mock):
        from papaye.views.simple import PackageNotFoundView

        mock.return_value = FakeGRequestResponse(404, '')

        view = PackageNotFoundView(self.request, 'Package')
        view.proxy = True
        view.request.matchdict['traverse'] = ('unknowpackage',)

        result = view()
        self.assertEqual(mock.call_count, 1)
        self.assertIsInstance(result, HTTPNotFound)


class ReleaseNotFoundViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)
        registry = self.request.registry
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'memory://',
        }
        self.config.include('pyramid_jinja2')
        self.config.add_jinja2_search_path("papaye:templates")
        set_cache_regions_from_settings(registry.settings)

    def test_get_params(self):
        from papaye.views.simple import ReleaseNotFoundView

        self.request.matchdict['traverse'] = ('one', 'two', 'three')
        view = ReleaseNotFoundView(self.request, 'Release')

        result = view.get_params()
        self.assertEqual(result, ('one', 'two'))

    def test_make_redirection(self):
        from papaye.views.simple import ReleaseNotFoundView
        from papaye.models import ReleaseFile

        view = ReleaseNotFoundView(self.request, 'File')
        pypi_result = {
            'urls': [{
                'filename': 'fakefilename.tar.gz',
            }]
        }

        result = view.make_redirection(b'', FakeGRequestResponse(200, bytes(json.dumps(pypi_result), 'utf-8')))
        self.assertIn('objects', result)
        self.assertEqual(len(result['objects']), 1)
        self.assertIsInstance(result['objects'][0][1], ReleaseFile)


class ReleaseFileNotFoundViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)
        registry = self.request.registry
        registry.settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'memory://',
        }
        set_cache_regions_from_settings(registry.settings)

    def test_get_params(self):
        from papaye.views.simple import ReleaseFileNotFoundView

        self.request.matchdict['traverse'] = ('one', 'two', 'three')
        view = ReleaseFileNotFoundView(self.request, 'Release')

        result = view.get_params()
        self.assertEqual(result, ('one', 'two'))

    def test_make_redirection(self):
        from papaye.views.simple import ReleaseFileNotFoundView

        self.request.matchdict['traverse'] = ('package', 'release', 'releasefile.tar.gz')
        view = ReleaseFileNotFoundView(self.request, 'File')
        pypi_result = {
            'urls': [{
                'filename': 'releasefile.tar.gz',
                'url': 'http://example.com/releasefile.tar.gz'
            }, {
                'filename': 'releasefile2.tar.gz',
                'url': 'http://example.com/releasefile2.tar.gz'
            }]
        }

        result = view.make_redirection('', FakeGRequestResponse(200, bytes(json.dumps(pypi_result), 'utf-8')))
        self.assertIsInstance(result, HTTPTemporaryRedirect)
        self.assertEqual(result.location, 'http://example.com/releasefile.tar.gz')

    def test_make_redirection_no_present_in_pypi(self):
        from papaye.views.simple import ReleaseFileNotFoundView

        self.request.matchdict['traverse'] = ('package', 'release', 'releasefile3.tar.gz')
        view = ReleaseFileNotFoundView(self.request, 'File')
        pypi_result = {
            'urls': [{
                'filename': 'releasefile.tar.gz',
                'url': 'http://example.com/releasefile.tar.gz'
            }, {
                'filename': 'releasefile2.tar.gz',
                'url': 'http://example.com/releasefile2.tar.gz'
            }]
        }

        result = view.make_redirection('', FakeGRequestResponse(200, bytes(json.dumps(pypi_result), 'utf-8')))

        self.assertIsInstance(result, HTTPNotFound)


class UploadReleaseViewTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)

    def test_upload_release(self):
        from papaye.models import Root, Package, Release, ReleaseFile
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO()
        uploaded_file.write(b"content")
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
        self.assertTrue('my_package' in root)
        self.assertIsInstance(root['my_package'], Package)
        self.assertTrue(root['my_package'].releases.get('1.0', False))
        self.assertIsInstance(root['my_package']['1.0'], Release)
        self.assertTrue(root['my_package']['1.0'].release_files.get('foo.tar.gz', b''))
        self.assertIsInstance(root['my_package']['1.0']['foo.tar.gz'], ReleaseFile)
        self.assertEqual(root['my_package']['1.0']['foo.tar.gz'].md5_digest, "Fake MD5")

    def test_upload_release_already_exists(self):
        from papaye.models import Root, Package, Release, ReleaseFile
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO()
        uploaded_file.write(b"content")
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

        #Create initial release
        package = Package('my_package')
        package['1.0'] = Release('1.0', '1.0')
        package['1.0']['foo.tar.gz'] = ReleaseFile('foo.tar.gz', b'')
        root['my_package'] = package

        view = UploadView(root, self.request)
        result = view()

        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 409)

    def test_upload_release_multiple_releasefile(self):
        from papaye.models import Root, Package, Release, ReleaseFile
        from papaye.views.simple import UploadView

        # Create a fake test file
        uploaded_file = io.BytesIO()
        uploaded_file.write(b"content")
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

        #Create initial release
        package = Package('my_package')
        package['1.0'] = Release('1.0', '1.0')
        package['1.0']['foo.tar.gz'] = ReleaseFile('foo.tar.gz', b'')
        root['my_package'] = package

        view = UploadView(root, self.request)
        result = view()

        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 200)
        self.assertTrue('my_package' in root)
        self.assertIsInstance(root['my_package'], Package)
        self.assertTrue(root['my_package'].releases.get('1.0', False))
        self.assertIsInstance(root['my_package']['1.0'], Release)
        self.assertTrue(root['my_package']['1.0'].release_files.get('foo.tar.gz', b''))
        self.assertIsInstance(root['my_package']['1.0']['foo.tar.gz'], ReleaseFile)
        self.assertTrue(root['my_package']['1.0'].release_files.get('foo.zip', b''))
        self.assertIsInstance(root['my_package']['1.0']['foo.zip'], ReleaseFile)


class ReleaseFileNotUpToDate(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)

    def test_get_params(self):
        from papaye.views.simple import ReleaseFileNotUpToDateView

        self.request.matchdict['traverse'] = ('package', )
        view = ReleaseFileNotUpToDateView(self.request, 'File')

        result = view.get_params()
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, ('package', ))

    def test_format_url(self):
        from papaye.views.simple import ReleaseFileNotUpToDateView

        view = ReleaseFileNotUpToDateView(self.request, 'File')
        result = view.format_url('http://example.com#md5=23456')

        self.assertEqual(result, 'http://example.com?check_update=false#md5=23456')

    def test_format_url_without_md5(self):
        from papaye.views.simple import ReleaseFileNotUpToDateView

        view = ReleaseFileNotUpToDateView(self.request, 'File')
        result = view.format_url('http://example.com')

        self.assertEqual(result, 'http://example.com?check_update=false')
