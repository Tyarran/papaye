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
            'zodbconn.uri': 'memory:///blobstorage_dir=packages',
        }
        set_cache_regions_from_settings(registry.settings)
        self.config.include('pyramid_zodbconn')

    @patch('requests.get')
    def test_get_last_remote_version_without_proxy(self, mock):
        from papaye.models import Package

        fake_response = Response(status=200, body='{"info": {"version": "1.0"}}')
        mock.return_value = fake_response

        # Test data
        package = Package('test')

        result = Package.get_last_remote_version(False, package.name)

        self.assertEqual(mock.call_count, 0)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_last_remote_version_with_proxy(self, mock):
        from papaye.models import Package

        fake_response = FakeGRequestResponse(status_code=200, content=b'{"info": {"version": "1.0"}}')
        mock.return_value = fake_response

        # Test data
        package = Package('test')

        result = Package.get_last_remote_version(True, package.name)

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

        result = Package.get_last_remote_version(True, package.name)

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

    def test_by_name(self):
        from papaye.models import Package
        from papaye.factories import repository_root_factory

        root = repository_root_factory(self.request)
        root['package1'] = Package(name='package1')

        result = Package.by_name('package1', self.request)
        self.assertEqual(result, root['package1'])

    def test_by_name_not_found(self):
        from papaye.models import Package

        result = Package.by_name('package1', self.request)
        self.assertEqual(result, None)

    def test_get_last_release(self):
        from papaye.models import Package, Release

        package = Package(name='package1')
        package.releases.update([('{}.0'.format(index), Release('', '{}.0'.format(index))) for index in range(1, 3)])
        result = package.get_last_release()
        self.assertEqual(result.version, '2.0')

    def test_get_last_release_with_minor(self):
        from papaye.models import Package, Release

        package = Package(name='package1')
        package.releases.update([('1.{}'.format(index), Release('', '1.{}'.format(index))) for index in range(1, 3)])
        result = package.get_last_release()
        self.assertEqual(result.version, '1.2')

    def test_get_last_release_with_alpha(self):
        from papaye.models import Package, Release

        package = Package(name='package1')
        package.releases.update([('1.0{}'.format(version), Release('', '1.0{}'.format(version)))
                                for version in ['', 'a1', 'a2', 'b1', 'b2', 'rc1']])
        result = package.get_last_release()
        self.assertEqual(result.version, '1.0')


class ReleaseTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        settings = {
            'zodbconn.uri': 'memory://',
        }
        self.config = testing.setUp(request=self.request, settings=settings)
        self.config.include('pyramid_zodbconn')

    def test_by_packagename(self):
        from papaye.models import Release, Package
        from papaye.factories import repository_root_factory

        root = repository_root_factory(self.request)
        root['package1'] = Package(name='package1')
        root['package1']['1.0'] = Release('1.0', '1.0')

        result = Release.by_packagename('package1', self.request)
        self.assertEqual(result, [root['package1']['1.0'], ])

    def test_by_packagename_not_found(self):
        from papaye.models import Release

        result = Release.by_packagename('package1', self.request)
        self.assertEqual(result, None)


class UserTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        settings = {
            'zodbconn.uri': 'memory://',
        }
        self.config = testing.setUp(request=self.request, settings=settings)
        self.config.include('pyramid_zodbconn')

    def test_hash_password(self):
        from papaye.models import User
        expected = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a'
        expected += '2ea6d103fd07c95385ffab0cacbc86'

        result = User('a_user', 'password')
        self.assertEqual(result.password, expected)

    def test_by_username(self):
        from papaye.models import User
        from papaye.factories import user_root_factory

        root = user_root_factory(self.request)
        root['a_user'] = User('a_user', 'password')

        result = User.by_username('a_user', self.request)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, 'a_user')

    def test_by_username_without_result(self):
        from papaye.models import User

        result = User.by_username('a_user', self.request)

        self.assertIsNone(result)
