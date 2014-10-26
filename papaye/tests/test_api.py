import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound


class APIPackageViewTest(unittest.TestCase):

    def setUp(self):
        settings = {'papaye.proxy': False}
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request, settings=settings)
        self.config.include('pyramid_zodbconn')

    def test_get_packages(self):
        from papaye.views.api import list_packages
        from papaye.models import Package, Root, Release
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['1.0'] = Release('1.0', '1.0', {
            'summary': 'The package 1',
            'description': 'A description',
        })
        root['package2']['1.0'] = Release('1.0', '1.0', {
            'summary': 'The package 2',
            'description': 'A description',
        })
        expected = [{
            'name': 'package1',
            'summary': 'The package 1',
        }, {
            'name': 'package2',
            'summary': 'The package 2',
        }, ]
        self.request.context = root

        result = list_packages(self.request)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dict)
        self.assertEqual([dict(element) for element in result], expected)

    def test_get_packages_with_no_package_in_database(self):
        from papaye.views.api import list_packages
        from papaye.models import Root
        root = Root()
        self.request.context = root

        result = list_packages(self.request)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

    def test_get_package(self):
        from papaye.views.api import get_package
        from papaye.models import Package, Root, Release
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['1.0'] = Release('1.0', '1.0', {
            'summary': 'The package 1',
            'description': 'A description',
        })
        root['package2']['1.0'] = Release('1.0', '1.0', {
            'summary': 'The package 2',
            'description': 'A description',
        })
        self.request.context = root
        self.request.matchdict = {'package_name': 'package1'}

        result = get_package(self.request)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'package1')
        self.assertIn('metadata', result)

    def test_get_package_unknown(self):
        from papaye.views.api import get_package
        from papaye.models import Root
        root = Root()
        self.request.context = root
        self.request.matchdict = {'package_name': 'package1'}

        result = get_package(self.request)

        self.assertIsInstance(result, HTTPNotFound)

    def test_get_package_by_version(self):
        from papaye.views.api import get_package_by_version
        from papaye.models import Package, Root, Release
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['1.0'] = Release('1.0', '1.0', {
            'summary': 'The package 1',
            'description': 'A description',
        })
        root['package2']['1.0'] = Release('1.0', '1.0', {'summary': 'The package 2', 'description': ''})
        self.request.context = root
        self.request.matchdict = {'package_name': 'package1', 'version': '1.0'}

        result = get_package_by_version(self.request)

        self.assertIsInstance(result, dict)

    def test_get_package_by_version_with_unknown_package(self):
        from papaye.views.api import get_package_by_version
        from papaye.models import Package, Root, Release
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['1.0'] = Release('1.0', '1.0', {'summary': 'The package 1'})
        root['package2']['1.0'] = Release('1.0', '1.0', {'summary': 'The package 2'})
        self.request.context = root
        self.request.matchdict = {'package_name': 'package3', 'version': '1.0'}

        result = get_package_by_version(self.request)

        self.assertIsInstance(result, HTTPNotFound)

    def test_get_package_by_version_with_unknown_release(self):
        from papaye.views.api import get_package_by_version
        from papaye.models import Package, Root, Release
        root = Root()
        root['package1'] = Package(name='package1')
        root['package2'] = Package(name='package2')
        root['package1']['1.0'] = Release('1.0', '1.0', {'summary': 'The package 1'})
        root['package2']['1.0'] = Release('1.0', '1.0', {'summary': 'The package 2'})
        self.request.context = root
        self.request.matchdict = {'package_name': 'package2', 'version': '2.0'}

        result = get_package_by_version(self.request)

        self.assertIsInstance(result, HTTPNotFound)
