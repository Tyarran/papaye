import shutil
import tempfile
import types
import unittest

from os import mkdir
from os.path import join
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPTemporaryRedirect
from pyramid.response import FileResponse
from pyramid.threadlocal import get_current_request, get_current_registry

from papaye.views import SimpleView, PackageNotFoundException, ReleaseNotFoundException


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
        registry.settings = {'papaye.repository': self.repository}
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
        self.assertIsInstance(response, types.GeneratorType)
        self.assertEqual([p for p in response],
                         [('package1', '/simple/package1'),
                          ('package2', '/simple/package2')])

    def test_list_releases(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        view = SimpleView(request)
        response = view.list_releases()
        self.assertIsInstance(response, tuple)
        self.assertTrue(len(response) == 2)
        self.assertIsInstance(response[0], types.GeneratorType)
        self.assertEqual([p for p in response[0]],
                         [('file-1.0.tar.gz', '/simple/package1/file-1.0.tar.gz', )])
        self.assertEqual(response[1], 'package1')

    def test_list_releases_with_bad_package(self):
        request = get_current_request()
        request.matchdict['package'] = 'package10'
        view = SimpleView(request)
        self.assertRaises(PackageNotFoundException, view.list_releases)

    def test_download_release(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        request.matchdict['release'] = 'file-1.0.tar.gz'
        view = SimpleView(request)
        response = view.download_release()
        self.assertIsInstance(response, FileResponse)

    def test_download_release_with_bad_release(self):
        request = get_current_request()
        request.matchdict['package'] = 'package1'
        request.matchdict['release'] = 'file1.tar.gz'
        view = SimpleView(request)
        self.assertRaises(ReleaseNotFoundException, view.download_release)

    def test__call__simple_route(self):
        request = get_current_request()
        request.matched_route = FakeMatchedDict('simple')
        view = SimpleView(request)
        result = view()
        self.assertIsInstance(result, dict)
        self.assertIn('objects', result)

    def test__call__simple_release_route(self):
        request = get_current_request()
        request.matched_route = FakeMatchedDict('simple_release')
        request.matchdict['package'] = 'package1'
        view = SimpleView(request)
        result = view()
        self.assertIsInstance(result, dict)
        self.assertIn('objects', result)
        self.assertIn('package', result)
        self.assertEqual(result['package'], 'package1')

    def test__call__simple_release_route_with_bad_package_without_proxy(self):
        request = get_current_request()
        request.matched_route = FakeMatchedDict('simple_release')
        request.matchdict['package'] = 'package10'
        view = SimpleView(request)
        result = view()
        self.assertIsInstance(result, HTTPNotFound)

    def test__call__simple_release_route_with_bad_package_with_proxy(self):
        request = get_current_request()
        request.matched_route = FakeMatchedDict('simple_release')
        request.matchdict['package'] = 'package10'
        registry = get_current_registry()
        registry.settings['papaye.proxy'] = 'true'
        view = SimpleView(request)
        result = view()
        self.assertIsInstance(result, HTTPTemporaryRedirect)
        self.assertEqual(result.location, 'http://pypi.python.org/simple/package10/')

    def test__call__download_release_route(self):
        request = get_current_request()
        request.matched_route = FakeMatchedDict('download_release')
        request.matchdict['package'] = 'package1'
        request.matchdict['release'] = 'file-1.0.tar.gz'
        view = SimpleView(request)
        result = view()
        self.assertIsInstance(result, FileResponse)
