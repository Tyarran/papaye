import colander
import unittest

from pyramid import testing
from pyramid.threadlocal import get_current_request

from papaye.factories import models as factories


class DummySerializer(object):
    string = colander.SchemaNode(colander.String())
    number = colander.SchemaNode(colander.Integer())


class SerializerTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

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


class ReleaseAPISerializerTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()
        self.maxDiff = None

    def test_instanciate(self):
        from papaye.serializers import ReleaseAPISerializer

        serializer = ReleaseAPISerializer(request=self.request)

        self.assertIsInstance(serializer, ReleaseAPISerializer)
        self.assertTrue(getattr(serializer, 'request', None))
        self.assertEqual(serializer.request, self.request)

    def test_serialize(self):
        from papaye.serializers import ReleaseAPISerializer
        request = get_current_request()
        serializer = ReleaseAPISerializer(request=self.request)
        package = factories.PackageFactory(name='package')
        package['1.0'] = factories.ReleaseFactory(
            version='1.0',
            metadata={
                'summary': 'The package',
                'description': 'A description',
            },
            package=package,
        )
        release = factories.ReleaseFactory(
            version='2.0',
            metadata={
                'summary': 'The package',
                'description': 'A description',
            },
            package=package,
        )
        package['2.0'] = release
        release_file = factories.ReleaseFileFactory(
            name='package-1.0.tar.gz',
            content=b'',
            release=release,
        )
        package['1.0']['package-1.0.tar.gz'] = release_file
        expected = {
            'name': package.name,
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
            'download_url': request.static_url(release_file.path),
            'release_files': [{
                'size': '0',
                'filename': release_file.filename,
                'url': request.static_url(release_file.path),
                'version': '1.0',
                'upload_date': str(release_file.upload_date),
            }],
            'other_releases': [{
                'url': 'http://example.com/#/browse/package/2.0',
                'version': '2.0',
            }]
        }

        result = serializer.serialize(package['1.0'])

        for key, value in result.items():
            assert value == expected[key]

    def test_serialize_with_metadata_is_none(self):
        from papaye.serializers import ReleaseAPISerializer
        request = get_current_request()
        serializer = ReleaseAPISerializer(request=self.request)
        package = factories.PackageFactory(name='package')
        release1 = factories.ReleaseFactory(
            version='1.0',
            metadata=None,
            package=package,
        )
        package['1.0'] = release1

        release2 = factories.ReleaseFactory(
            version='2.0',
            metadata={
                'summary': 'The package',
                'description': 'A description',
            },
            package=package,
        )
        package['2.0'] = release2

        release_file = factories.ReleaseFileFactory(
            filename='package-1.0.tar.gz',
            release=release1,
        )
        package['1.0']['package-1.0.tar.gz'] = release_file
        expected = {
            'name': package.name,
            'version': '1.0',
            'gravatar_hash': None,
            'metadata': {
                'version': None,
                'author': None,
                'author_email': None,
                'home_page': None,
                'keywords': [],
                'license': None,
                'summary': None,
                'maintainer': None,
                'maintainer_email': None,
                'description': None,
                'platform': None,
                'classifiers': [], 'name': None,
            },
            'download_url': request.static_url(release_file.path),
            'release_files': [{
                'size': '9',
                'filename': 'package-1.0.tar.gz',
                'url': request.static_url(release_file.path),
                'version': '1.0',
                'upload_date': str(package['1.0']['package-1.0.tar.gz'].upload_date),
            }],
            'other_releases': [{
                'url': 'http://example.com/#/browse/package/2.0',
                'version': '2.0',
            }]
        }

        result = serializer.serialize(package['1.0'])

        for key, value in result.items():
            assert value == expected[key]
