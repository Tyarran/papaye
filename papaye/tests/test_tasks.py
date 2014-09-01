import io
import shutil
import tempfile
import unittest

from mock import patch
from pyramid import testing
from pyramid.threadlocal import get_current_request

from papaye.tests.tools import (
    FakeGRequestResponse,
    disable_cache,
    get_db_connection,
    get_resource,
)


class TestDownloadTask(unittest.TestCase):

    def setUp(self):
        self.blob_dir = tempfile.mkdtemp()
        request = testing.DummyRequest()
        settings = disable_cache()
        self.config = testing.setUp(request=request, settings=settings)
        self.conn = get_db_connection(self.blob_dir)

    def tearDown(self):
        shutil.rmtree(self.blob_dir)

    @patch('requests.get')
    @patch('papaye.tasks.download.get_connection')
    def test_download_release_from_pypi(self, get_connection_mock, request_mock):
        from papaye.tasks.download import download_release_from_pypi
        from papaye.factories import repository_root_factory
        request = get_current_request()
        get_connection_mock.return_value = self.conn

        json_response = open(get_resource('pyramid.json'), 'rb')
        release_file_content = open(get_resource('pyramid-1.5.tar.gz'), 'rb')
        request_mock.side_effect = [
            FakeGRequestResponse(200, b'', 'http://pypi.python.org/simple/pyramid/'),
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, release_file_content.read()),
        ]

        download_release_from_pypi(request.registry.settings, 'pyramid', '1.5')
        self.assertEqual(request_mock.call_count, 3)
        root = repository_root_factory(self.conn)
        self.assertIn('pyramid', root)
        self.assertIn('1.5', root['pyramid'].releases)
        self.assertIn('pyramid-1.5.tar.gz', root['pyramid']['1.5'].release_files)
        release_file = root['pyramid']['1.5']['pyramid-1.5.tar.gz']
        self.assertEqual(release_file.md5_digest, "8747658dcbab709a9c491e43d3b0d58b")
        self.assertEqual(release_file.filename, "pyramid-1.5.tar.gz")
        self.assertEqual(release_file.size, 2413504)
        self.assertEqual(list(root['pyramid'].releases.keys()), ['1.5', ])

    @patch('requests.get')
    @patch('papaye.tasks.download.get_connection')
    def test_download_release_from_pypi_with_bad_md5(self, get_connection_mock, request_mock):
        from papaye.tasks.download import download_release_from_pypi
        from papaye.factories import repository_root_factory
        request = get_current_request()
        get_connection_mock.return_value = self.conn

        json_response = open(get_resource('pyramid.json'), 'rb')
        release_file_content = io.BytesIO(b'corrupted_file')
        request_mock.side_effect = [
            FakeGRequestResponse(200, b'', 'http://pypi.python.org/simple/pyramid/'),
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, release_file_content.read()),
        ]

        self.assertRaises(IOError, download_release_from_pypi, request.registry.settings, 'pyramid', '1.5')
        self.assertEqual(request_mock.call_count, 3)
        root = repository_root_factory(self.conn)
        self.assertNotIn('pyramid', root)
