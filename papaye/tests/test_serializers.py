import colander
import unittest

from pyramid import testing
from pyramid.threadlocal import get_current_registry

from papaye.tests.tools import FakeRoute, disable_cache


class DummySerializer(object):
    string = colander.SchemaNode(colander.String())
    number = colander.SchemaNode(colander.Integer())


class SerializerTest(unittest.TestCase):

    def test_instanciate(self):
        from papaye.serializers import Serializer

        class TestSerializer(DummySerializer, Serializer):
            pass

        serializer = TestSerializer('Fake request')

        self.assertTrue(getattr(serializer, 'schema', None))

    def test_schema(self):
        from papaye.serializers import Serializer

        class TestSerializer(DummySerializer, Serializer):
            pass

        serializer = TestSerializer(None)
        schema = getattr(serializer, 'schema')

        self.assertTrue(schema)
        self.assertIsInstance(serializer.schema, colander.SchemaNode)
        self.assertEqual(len(serializer.schema.children), 2)

    def test_schema_without_node(self):
        from papaye.serializers import Serializer

        class TestSerializer(Serializer):
            pass

        serializer = TestSerializer(None)
        schema = getattr(serializer, 'schema')

        self.assertFalse(schema)


class PackageAPISerializerTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest(matched_route=FakeRoute('simple'))
        self.config = testing.setUp(request=self.request)
        self.config.add_route('simple', '/simple/*traverse', factory='papaye.factories:repository_root_factory')
        registry = get_current_registry()
        registry.settings = disable_cache()

    def test_instanciate(self):
        from papaye.serializers import PackageAPISerializer

        serializer = PackageAPISerializer(request=self.request)

        self.assertIsInstance(serializer, PackageAPISerializer)
        self.assertTrue(getattr(serializer, 'request', None))
        self.assertEqual(serializer.request, self.request)

    def test_serialize(self):
        from papaye.serializers import PackageAPISerializer
        from papaye.models import Package, Release, ReleaseFile
        serializer = PackageAPISerializer(request=self.request)
        package = Package(name='package')
        package['1.0'] = Release('1.0', '1.0', {
            'summary': 'The package',
            'description': 'A description',
        })
        package['1.0']['package-1.0.tar.gz'] = ReleaseFile('package-1.0.tar.gz', b'')
        expected = {
            'name': 'package',
            'version': '1.0',
            'gravatar_hash': None,
            'metadata': {
                'summary': 'The package',
                'description': {'html': True, 'content': '<p>A description</p>\n'},
                'version': None,
                'author': None,
                'author_email': None,
                'home_page': None,
                'keywords': [],
                'license': None,
                'maintainer': None,
                'maintainer_email': None,
                'platform': None,
                'classifiers': [],
                'name': None,
            },
            'download_url': 'http://example.com/simple/package/1.0/package-1.0.tar.gz/',
        }

        result = serializer.serialize(package)

        self.assertEqual(result, expected)
