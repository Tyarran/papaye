import json
import unittest

from mock import patch
from pyramid import testing
from requests.exceptions import ConnectionError

from papaye.tests.tools import (
    FakeGRequestResponse,
    disable_cache,
    get_resource,
    remove_blob_dir,
    set_database_connection,
)


class ProxyTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.blob_dir = set_database_connection(self.request)
        settings = disable_cache()
        self.config = testing.setUp(request=self.request, settings=settings)
        with open(get_resource('pyramid.json'), 'rb') as pyramid_json:
            self.pypi_response = FakeGRequestResponse(200, pyramid_json.read())

    def tearDown(self):
        remove_blob_dir(self.blob_dir)

    @patch('requests.get')
    def test_get_remote_informations(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = self.pypi_response
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.get_remote_informations(url)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['info']['name'], 'pyramid')

    @patch('requests.get')
    def test_get_remote_informations_404(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.get_remote_informations(url)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_remote_informations_connection_error(self, mock):
        from papaye.proxy import PyPiProxy
        mock.side_effect = ConnectionError
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.get_remote_informations(url)
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
        self.assertEqual(result['1.5'].release_files.values()[0].pypi_url,
                         "https://pypi.python.org/packages/source/p/pyramid/pyramid-1.5.tar.gz")
        self.assertIsNotNone(result['1.5'].metadata)
        self.assertIsInstance(result['1.5'].metadata, dict)

    @patch('requests.get')
    def test_build_repository_404_error(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.build_repository()

        self.assertIsNone(result)

    @patch('requests.get')
    def test_smart_merge(self, mock):
        from papaye.proxy import PyPiProxy
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        mock.return_value = self.pypi_response
        root = repository_root_factory(self.request)

        # Existing releases
        root['pyramid'] = Package(name='pyramid')
        root['pyramid']['1.4'] = Release(name='1.4', version='1.4')
        root['pyramid']['1.4']['pyramid-1.4.tar.gz'] = ReleaseFile(
            filename='pyramid-1.4.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        package = Package(name='pyramid')
        package['1.5'] = Release(name='1.5', version='1.5')
        package['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.smart_merge(root, package)

        self.assertEqual([key for key in result.releases.keys()], ['1.4', '1.5'])

    @patch('requests.get')
    def test_smart_merge_with_existing_release(self, mock):
        from papaye.proxy import PyPiProxy
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        mock.return_value = self.pypi_response
        root = repository_root_factory(self.request)

        # Existing releases
        package = Package(name='pyramid')
        package['1.5'] = Release(name='1.5', version='1.5')
        package['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        package = Package(name='pyramid')
        package['1.5'] = Release(name='1.5', version='1.5')
        package['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.smart_merge(root, package)

        self.assertEqual([key for key in result.releases.keys()], ['1.5', ])
        self.assertEqual(result['1.5']['pyramid-1.5.tar.gz'].md5_digest, '12345')

    @patch('requests.get')
    def test_smart_merge_with_unknown_package(self, mock):
        from papaye.proxy import PyPiProxy
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        mock.return_value = self.pypi_response
        root = repository_root_factory(self.request)

        package = Package(name='pyramid')
        package['1.5'] = Release(name='1.5', version='1.5')
        package['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        proxy = PyPiProxy(self.request, 'pyramid')
        result = proxy.smart_merge(root, package)

        self.assertEqual([key for key in result.releases.keys()], ['1.5', ])
        self.assertEqual(result, package)
