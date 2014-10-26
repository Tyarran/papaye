import json
import unittest

from docutils.core import publish_parts

from papaye.tests.tools import get_resource


class MetadataTest(unittest.TestCase):

    def test_deserialize_from_pypi(self):
        # Test response
        with open(get_resource('pyramid.json'), 'r') as json_file:
            cstruct = json.loads(json_file.read())['info']
        from papaye.schemas import Metadata
        schema = Metadata()
        expected_keys = sorted([
            'version',
            'author',
            'author_email',
            'home_page',
            'keywords',
            'license',
            'summary',
            'maintainer',
            'maintainer_email',
            'description',
            'platform',
            'classifiers',
            'name',
        ])

        result = schema.deserialize(cstruct)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(expected_keys, sorted([key for key in result.keys()]))
        self.assertEqual(result['version'], '1.5')
        self.assertEqual(result['author'], 'Chris McDonough, Agendaless Consulting')
        self.assertEqual(result['author_email'], 'pylons-discuss@googlegroups.com')
        self.assertEqual(result['home_page'], 'http://pylonsproject.org')
        self.assertEqual(result['keywords'], ['web',  'wsgi',  'pylons', 'pyramid'])
        self.assertEqual(result['license'], 'BSD-derived (http://www.repoze.org/LICENSE.txt)')
        self.assertEqual(result['summary'], cstruct['summary'])
        self.assertEqual(result['maintainer'], None)
        self.assertEqual(result['maintainer_email'], None)
        self.assertEqual(
            result['description'],
            {
                'html': True,
                'content': publish_parts(cstruct['description'], writer_name='html')['fragment'],
            }
        )
        self.assertEqual(result['platform'], 'UNKNOWN')
        self.assertEqual(result['classifiers'], cstruct['classifiers'])
        self.assertEqual(result['name'], 'pyramid')

    def test_deserialize_from_setuptools(self):
        # Test response
        with open(get_resource('papaye_setuptools.json'), 'r') as json_file:
            cstruct = json.loads(json_file.read())
        from papaye.schemas import Metadata
        schema = Metadata()
        expected_keys = sorted([
            'version',
            'author',
            'author_email',
            'home_page',
            'keywords',
            'license',
            'summary',
            'maintainer',
            'maintainer_email',
            'description',
            'platform',
            'classifiers',
            'name',
        ])
        expected_classifiers = [
            "Programming Language :: Python",
            "Framework :: Pyramid",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ]

        result = schema.deserialize(cstruct)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(expected_keys, sorted([key for key in result.keys()]))
        self.assertEqual(result['version'], '0.1.3-dev')
        self.assertEqual(result['author'], 'Romain Commandé')
        self.assertEqual(result['author_email'], 'commande.romain@gmail.com')
        self.assertEqual(result['home_page'], 'https://github.com/rcommande/papaye')
        self.assertEqual(result['keywords'], ['web',  'wsgi', 'bfg', 'pylons', 'pyramid'])
        self.assertEqual(result['license'], 'UNKNOWN')
        self.assertEqual(result['summary'], cstruct['summary'])
        self.assertEqual(result['maintainer'], None)
        self.assertEqual(result['maintainer_email'], None)
        self.assertEqual(
            result['description'],
            {
                'html': True,
                'content': publish_parts(cstruct['description'], writer_name='html')['fragment'],
            }
        )
        self.assertEqual(result['platform'], 'UNKNOWN')
        self.assertEqual(result['classifiers'], expected_classifiers)
        self.assertEqual(result['name'], 'papaye')

    def test_deserialize_with_empty_metadata(self):
        from papaye.schemas import Metadata
        schema = Metadata()
        expected_keys = sorted([
            'version',
            'author',
            'author_email',
            'home_page',
            'keywords',
            'license',
            'summary',
            'maintainer',
            'maintainer_email',
            'description',
            'platform',
            'classifiers',
            'name',
        ])

        result = schema.deserialize({})
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(expected_keys, sorted([key for key in result.keys()]))
        self.assertEqual(result['version'], None)
        self.assertEqual(result['author'], None)
        self.assertEqual(result['author_email'], None)
        self.assertEqual(result['home_page'], None)
        self.assertEqual(result['keywords'], None)
        self.assertEqual(result['license'], None)
        self.assertEqual(result['summary'], None)
        self.assertEqual(result['maintainer'], None)
        self.assertEqual(result['maintainer_email'], None)
        self.assertEqual(result['description'], None)
        self.assertEqual(result['platform'], None)
        self.assertEqual(result['classifiers'], None)
        self.assertEqual(result['name'], None)
