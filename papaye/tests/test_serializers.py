import colander
import unittest


class DummySerializer(object):
    string = colander.SchemaNode(colander.String())
    number = colander.SchemaNode(colander.Integer())


class SerializerTest(unittest.TestCase):

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
