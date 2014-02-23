import StringIO
import shutil
import tempfile
import types
import unittest

from cgi import FieldStorage
from os import mkdir
from os.path import join, exists
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.registry import global_registry
from pyramid.response import FileResponse, Response
from pyramid.threadlocal import get_current_request, get_current_registry
from pyramid_beaker import set_cache_regions_from_settings

from papaye.views import SimpleView
from papaye.tests.tools import (
    create_db,
    TestRequest,
    TEST_RESOURCES,
    FakeProducer,
)


class SimpleTestView(unittest.TestCase):

    def setUp(self):
        self.request = TestRequest()
        self.request.db = create_db()
        self.config = testing.setUp(request=self.request)
        self.repository = tempfile.mkdtemp('repository')
        registry = get_current_registry()
        registry.settings = {
            'papaye.repository': self.repository,
            'cache.regions': 'pypi',
            'cache.type': 'memory',
            'cache.second.expire': '1',
            'cache.pypi': '5',
        }

        global_registry.producer = FakeProducer()
        set_cache_regions_from_settings(registry.settings)
        self.config.add_route('simple', 'simple/', static=True)
        mkdir(join(self.repository, 'package2'))
        mkdir(join(self.repository, 'package1'))
        open(join(self.repository, 'package1', 'file-1.0.tar.gz'), 'w').close()
        open(join(self.repository, 'package1', 'file2.data'), 'w').close()  # a bad file

    def tearDown(self):
        shutil.rmtree(self.repository)
        db = self.request.db
        for elem in db.all('id'):
            db.delete(elem)
        db.destroy()

    def test_list_packages(self):
        request = get_current_request()
        view = SimpleView(request)
        response = view.list_packages()
        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([p['name'] for p in response['objects']], ['package1', 'package2'])

    def test_list_releases(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        view = SimpleView(request)
        response = view.list_releases()
        self.assertIsInstance(response, dict)
        self.assertIn('objects', response)
        self.assertIn('package', response)
        self.assertIsInstance(response['objects'], types.GeneratorType)
        self.assertEqual([p['name'] for p in response['objects']],
                         ['file-1.0.tar.gz', ])
        self.assertEqual(response['package']['name'], 'package1')

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

    def test_upload_multiple_releases(self):
        for filename in ('Whoosh-2.6.0.tar.gz', 'Whoosh-2.6.0.zip'):
            upload_file = open(join(TEST_RESOURCES, filename), 'rb')
            storage = FieldStorage()
            storage.filename = filename
            storage.file = upload_file

            #Simulate file upload
            request = get_current_request()
            request.POST = {
                "content": storage,
            }

            view = SimpleView(request)
            result = view.upload_release()
            self.assertIsInstance(result, Response)
            self.assertEqual(result.status_int, 200)
            self.assertTrue(exists(join(self.repository, 'Whoosh')))
            self.assertTrue(exists(join(self.repository, 'Whoosh', filename)))

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
