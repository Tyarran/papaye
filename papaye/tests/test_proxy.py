import json
import unittest

from mock import patch
from pyramid import testing
from requests.exceptions import ConnectionError

from papaye.tests.tools import FakeGRequestResponse, get_resource


class ProxyTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        settings = {'zodbconn.uri': 'memory:///blobstorage_dir=packages'}
        self.config = testing.setUp(request=self.request, settings=settings)
        with open(get_resource('pyramid.json'), 'rb') as pyramid_json:
            self.pypi_response = FakeGRequestResponse(200, pyramid_json.read())
        self.config.include('pyramid_zodbconn')

    @patch('requests.get')
    def test_get_remote_informations(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = self.pypi_response

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.get_remote_informations()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['info']['name'], 'pyramid')

    @patch('requests.get')
    def test_get_remote_informations_404(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.get_remote_informations()
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_remote_informations_connection_error(self, mock):
        from papaye.proxy import PyPiProxy
        mock.side_effect = ConnectionError

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.get_remote_informations()
        self.assertIsNone(result)

    @patch('requests.get')
    def test_build_repository(self, mock):
        from papaye.proxy import PyPiProxy
        from papaye.models import Package, ReleaseFile
        mock.return_value = self.pypi_response
        info_dict = json.loads(self.pypi_response.content.decode('utf-8'))

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.build_repository()

        self.assertIsInstance(result, Package)
        for release in result.releases.values():
            self.assertIn(release.__name__, info_dict['releases'].keys())
        self.assertEqual(len(result.releases.keys()), len(info_dict['releases'].keys()))
        self.assertEqual(len(result['1.5'].release_files.keys()), 1)
        self.assertIsInstance(result['1.5'].release_files.values()[0], ReleaseFile)
        self.assertTrue(getattr(result['1.5'].release_files.values()[0], 'pypi_url', None))

    @patch('requests.get')
    def test_build_repository_404_error(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.build_repository()

        self.assertIsNone(result)
