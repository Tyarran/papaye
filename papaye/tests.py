import shutil
import tempfile
import types
import unittest
import StringIO

from cgi import FieldStorage
from os import mkdir
from os.path import join, exists
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.response import FileResponse, Response
from pyramid.threadlocal import get_current_request, get_current_registry
from pyramid_beaker import set_cache_regions_from_settings

from papaye.views import SimpleView


class FakeMatchedDict(object):

    def __init__(self, name):
        self.name = name


class TestRequest(testing.DummyRequest):

    def __init__(self, *args, **kwargs):
        super(TestRequest, self).__init__(*args, **kwargs)
        self.matched_route = FakeMatchedDict('')


class SimpleTestView(unittest.TestCase):

    def setUp(self):
        request = TestRequest()
        self.config = testing.setUp(request=request)
        self.repository = tempfile.mkdtemp('repository')
        registry = get_current_registry()
        registry.settings = {
            'papaye.repository': self.repository,
            'cache.regions': 'pypi',
            'cache.type': 'memory',
            'cache.second.expire': '1',
            'cache.pypi': '5',
        }
        set_cache_regions_from_settings(registry.settings)
        self.config.add_route('simple', 'simple/', static=True)
        mkdir(join(self.repository, 'package2'))
        mkdir(join(self.repository, 'package1'))
        open(join(self.repository, 'package1', 'file-1.0.tar.gz'), 'w').close()
        open(join(self.repository, 'package1', 'file2.data'), 'w').close()  # a bad file

    def tearDown(self):
        shutil.rmtree(self.repository)

    def test_list_packages(self):
        request = get_current_request()
        view = SimpleView(request)
        response = view.list_packages()
        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([p for p in response['objects']],
                         [('package1', '/simple/package1'),
                          ('package2', '/simple/package2')])

    def test_list_releases(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        view = SimpleView(request)
        response = view.list_releases()
        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIn('package', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([p for p in response['objects']],
                         [('file-1.0.tar.gz', '/simple/package1/file-1.0.tar.gz', )])
        self.assertEqual(response['package'], 'package1')

    def test_list_releases_with_bad_package(self):
        request = get_current_request()
        request.matchdict['package'] = 'package10'
        view = SimpleView(request)
        result = view.list_releases()
        self.assertIsInstance(result, HTTPNotFound)

    def test_list_releases_with_bad_package_and_actived_proxy(self):
        request = get_current_request()
        registry = get_current_registry()
        registry.settings['papaye.proxy'] = 'true'
        package = 'package10'
        request.matchdict['package'] = package
        view = SimpleView(request)
        result = view.list_releases()
        self.assertIsInstance(result, HTTPTemporaryRedirect)
        self.assertEqual(result.location, 'http://pypi.python.org/simple/{}/'.format(package))

    def test_download_release(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        request.matchdict['release'] = 'file-1.0.tar.gz'
        view = SimpleView(request)
        response = view.download_release()
        self.assertIsInstance(response, FileResponse)

    def test_download_bad_release(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        request.matchdict['release'] = 'file1.tar.gz'
        view = SimpleView(request)
        result = view.download_release()
        self.assertIsInstance(result, HTTPNotFound)

    def test_download_bad_release_with_proxy(self):
        request = get_current_request()
        registry = get_current_registry()
        registry.settings['papaye.proxy'] = 'true'
        request.matchdict['package'] = 'package1'
        request.matchdict['release'] = 'file1.tar.gz'
        view = SimpleView(request)
        result = view.download_release()
        self.assertIsInstance(result, HTTPTemporaryRedirect)
        self.assertEqual(result.location, 'http://pypi.python.org/simple/{}/{}/'.format(
            request.matchdict['package'],
            request.matchdict['release'],
        ))

    def test_upload_release(self):
        # Create a fake test file
        uploaded_file = StringIO.StringIO()
        uploaded_file.write("content")
        storage = FieldStorage()
        storage.filename = 'foo.tar.gz'
        storage.file = uploaded_file

        #Simulate file upload
        request = get_current_request()
        request.POST = {
            "content": storage,
        }

        view = SimpleView(request)
        result = view.upload_release()
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 200)
        self.assertTrue(exists(join(self.repository, 'foo')))
        self.assertTrue(exists(join(self.repository, 'foo', 'foo.tar.gz')))

    def test_upload_release_without_file(self):
        request = get_current_request()
        view = SimpleView(request)
        result = view.upload_release()

        self.assertEqual(result.status_int, 400)

    def test_upload_release_with_unothaurized_extension(self):
        uploaded_file = StringIO.StringIO()
        uploaded_file.write("content")
        storage = FieldStorage()
        storage.filename = 'foo.bar'
        storage.file = uploaded_file

        #Simulate file upload
        request = get_current_request()
        request.POST = {
            "content": storage,
        }
        request = get_current_request()
        view = SimpleView(request)
        result = view.upload_release()

        self.assertEqual(result.status_int, 400)
