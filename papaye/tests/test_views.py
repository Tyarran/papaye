#import StringIO
import io
import shutil
import tempfile
import types
import unittest
import webtest

from cgi import FieldStorage
from os import mkdir
from os.path import join, exists
from pyquery import PyQuery
from pyramid import testing
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.registry import global_registry
from pyramid.response import FileResponse, Response
from pyramid.threadlocal import get_current_request, get_current_registry
from pyramid_beaker import set_cache_regions_from_settings

#from papaye.views import SimpleView
from papaye.tests.tools import (
    FakeProducer,
    TEST_RESOURCES,
    TestRequest,
    create_db,
    create_test_app,
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
        shutil.rmtree(self.request.db.path, ignore_errors=True)

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
        uploaded_file = io.StringIO()
        uploaded_file.write("content")
        storage = FieldStorage()
        storage.filename = 'foo.tar.gz'
        storage.file = uploaded_file

        #Simulate file upload
        request = get_current_request()
        request.POST = {
            "content": storage,
            "some_metadata": "Fake Metadata",
            ":action": "upload_file",
        }

        view = SimpleView(request)
        result = view.upload_release()
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_int, 200)
        self.assertTrue(exists(join(self.repository, 'foo')))
        self.assertTrue(exists(join(self.repository, 'foo', 'foo.tar.gz')))
        data = self.request.db.get('release', 'foo.tar.gz', with_doc=True)['doc']
        self.assertIn('upload_time', data)
        self.assertIn('info', data)
        self.assertIn('some_metadata', data['info'])
        self.assertEqual(data['info']['some_metadata'], 'Fake Metadata')
        self.assertNotIn(':action', data['info'])
        self.assertNotIn('content', data['info'])

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
        uploaded_file = io.StringIO()
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

    def test_repository_is_up_to_date(self):
        from papaye.views import SimpleView
        package = {
            'type': 'package',
            'name': 'test_package',
        }
        release = {
            'type': 'release',
            'name': 'file-1.0.2.tar.gz',
            'package': 'test_package',
            'info': {
                'version': '1.0.2',
            }
        }
        self.request.db.insert(package)
        self.request.db.insert(release)
        request = get_current_request()
        view = SimpleView(request)

        remote_version = '1.0.3'
        result = view.repository_is_up_to_date(remote_version, 'test_package')
        self.assertFalse(result)

        remote_version = '1.0.1'
        result = view.repository_is_up_to_date(remote_version, 'test_package')
        self.assertTrue(result)

        remote_version = '1.0.2'
        result = view.repository_is_up_to_date(remote_version, 'test_package')
        self.assertTrue(result)

        remote_version = '1.0.2-alpha'
        result = view.repository_is_up_to_date(remote_version, 'test_package')
        self.assertTrue(result)

    def test_repository_is_up_to_date_with_preversion(self):
        from papaye.views import SimpleView
        package = {
            'type': 'package',
            'name': 'test_package',
        }
        release = {
            'type': 'release',
            'name': 'file-1.0.2-alpha2.tar.gz',
            'package': 'test_package',
            'info': {
                'version': '1.0.2-alpha2',
            }
        }
        self.request.db.insert(package)
        self.request.db.insert(release)
        request = get_current_request()
        view = SimpleView(request)

        remote_version = '1.0.2'
        result = view.repository_is_up_to_date(remote_version, 'test_package')
        self.assertFalse(result)


class SimpleFunctionnalTest(unittest.TestCase):

    def setUp(self):
        self.repository = tempfile.mkdtemp('repository')
        settings = {
            'papaye.repository': self.repository,
            'cache.regions': 'pypi',
            'cache.type': 'memory',
            'cache.second.expire': '1',
            'cache.pypi': '5',
            'codernity.url': 'file://%(here)s/papaye_database',
        }
        config = Configurator(settings=settings)
        self.db = create_db()
        config.scan('papaye.views')
        app = create_test_app(config)
        self.client = webtest.TestApp(app)

    def tearDown(self):
        shutil.rmtree(self.repository)
        shutil.rmtree(self.db.path, ignore_errors=True)

    def test_list_packages(self):
        response = self.client.get('/simple/')
        self.assertEqual(response.status_code, 200)

        title = response.pyquery('title')
        self.assertEqual(title.text(), 'Papaye Simple Index')

        expected_links_text = ['package1', 'package2']

        links = response.pyquery('a')
        self.assertEqual(len(links), 2)
        for index, link_element in enumerate(links):
            link = PyQuery(link_element)
            self.assertEqual(link.text(), expected_links_text[index])
            self.assertEqual(link.attr('href'), 'http://localhost/simple/{}'.format(expected_links_text[index]))

    def test_list_releases(self):
        response = self.client.get('/simple/package1/')
        self.assertEqual(response.status_code, 200)

        title = response.pyquery('title')
        self.assertEqual(title.text(), 'Papaye Simple Index')

        expected_link_text = 'file-1.0.tar.gz'

        links = response.pyquery('a')
        self.assertEqual(len(links), 1)

        self.assertEqual(links.eq(0).text(), expected_link_text)
        self.assertEqual(links.eq(0).attr('href'), 'file-1.0.tar.gz?md5=Fake MD5')
