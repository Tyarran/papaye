import io
import shutil
import tempfile
import unittest

from mock import patch
from pyramid import testing
from pyramid.threadlocal import get_current_request

from papaye.tests.tools import FakeGRequestResponse, get_resource


class TestDownloadTask(unittest.TestCase):

    def setUp(self):
        self.database_dir = tempfile.mkdtemp()
        request = testing.DummyRequest()
        settings = {
            'cache.regions': 'pypi',
            'cache.enabled': 'false',
            'zodbconn.uri': 'file://{0}/papaye.db?blobstorage_dir={0}/packages'.format(self.database_dir),
        }
        self.config = testing.setUp(request=request, settings=settings)
        self.config.include('pyramid_zodbconn')

    def tearDown(self):
        shutil.rmtree(self.database_dir)

    @patch('requests.get')
    def test_download_release_from_pypi(self, request_mock):
        from papaye.tasks.download import download_release_from_pypi
        from papaye.factories import repository_root_factory
        request = get_current_request()

        json_response = open(get_resource('pyramid.json'), 'r')
        release_file_content = open(get_resource('pyramid-1.5.tar.gz'), 'rb')
        request_mock.side_effect = [
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, release_file_content),
        ]

        download_release_from_pypi('http://example.com/', '1.5')
        self.assertEqual(request_mock.call_count, 2)
        root = repository_root_factory(request)
        self.assertIn('pyramid', root)
        self.assertIn('1.5', root['pyramid'].releases)
        self.assertIn('pyramid-1.5.tar.gz', root['pyramid']['1.5'].release_files)
        release_file = root['pyramid']['1.5']['pyramid-1.5.tar.gz']
        self.assertEqual(release_file.md5_digest, "8747658dcbab709a9c491e43d3b0d58b")
        self.assertEqual(release_file.filename, "pyramid-1.5.tar.gz")

    @patch('requests.get')
    def test_download_release_from_pypi_with_bad_md5(self, request_mock):
        from papaye.tasks.download import download_release_from_pypi
        from papaye.factories import repository_root_factory
        request = get_current_request()

        json_response = open(get_resource('pyramid.json'), 'r')
        release_file_content = io.BytesIO(b'corrupted_file')
        request_mock.side_effect = [
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, release_file_content),
        ]

        download_release_from_pypi('http://example.com/', '1.5')
        self.assertEqual(request_mock.call_count, 2)
        root = repository_root_factory(request)
        self.assertNotIn('pyramid', root)
