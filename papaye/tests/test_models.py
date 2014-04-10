import unittest

from mock import patch
from pyramid import testing
from pyramid.response import Response
from pyramid_beaker import set_cache_regions_from_settings

from papaye.tests.tools import FakeGRequestResponse, FakeRoute


class PackageTest(unittest.TestCase):

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
    def test_get_last_remote_version_without_proxy(self, mock):
        from papaye.models import Package

        fake_response = Response(status=200, body='{"info": {"version": "1.0"}}')
        mock.return_value = fake_response

        # Test data
        package = Package('test')

        result = package.get_last_remote_version(False)

        self.assertEqual(mock.call_count, 0)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_last_remote_version_with_proxy(self, mock):
        from papaye.models import Package

        fake_response = FakeGRequestResponse(status_code=200, content=b'{"info": {"version": "1.0"}}')
        mock.return_value = fake_response

        # Test data
        package = Package('test')

        result = package.get_last_remote_version(True)

        self.assertEqual(mock.call_count, 1)
        self.assertIsNotNone(result)
        self.assertEqual(result, '1.0')

    @patch('requests.get')
    def test_get_last_remote_version_with_proxy_404(self, mock):
        from papaye.models import Package

        fake_response = FakeGRequestResponse(status_code=404, content=b'{"info": {"version": "1.0"}}')
        mock.return_value = fake_response

        # Test data
        package = Package('test')

        result = package.get_last_remote_version(True)

        self.assertEqual(mock.call_count, 1)
        self.assertIsNone(result)

    def test_repository_is_up_to_date(self):
        from papaye.models import Package, Release

        # Test package
        package = Package(name='package1')
        release = Release(name='1.0', version='1.0')
        package['release'] = release

        self.assertTrue(package.repository_is_up_to_date('1.0'))
        self.assertTrue(package.repository_is_up_to_date('0.9'))
        self.assertTrue(package.repository_is_up_to_date('1.0a'))
        self.assertFalse(package.repository_is_up_to_date('1.1'))
        self.assertFalse(package.repository_is_up_to_date('1.1a'))
        self.assertTrue(package.repository_is_up_to_date(''))
        self.assertTrue(package.repository_is_up_to_date(None))
