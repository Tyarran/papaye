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
        self.root = self.conn.root()['papaye_root']['repository']

    def tearDown(self):
        shutil.rmtree(self.blob_dir)

    @patch('requests.get')
    @patch('papaye.tasks.download.get_connection')
    def test_download_release_from_pypi(self, get_connection_mock, request_mock):
        from papaye.tasks.download import download_release_from_pypi
        request = get_current_request()
        get_connection_mock.return_value = self.conn

        json_response = open(get_resource('pyramid.json'), 'rb')
        json_request_response = open(get_resource('pyramid1.4.json'), 'rb')
        release_file_content = open(get_resource('pyramid-1.5.tar.gz'), 'rb')
        request_mock.side_effect = [
            FakeGRequestResponse(200, b'', 'http://pypi.python.org/simple/pyramid/'),
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, json_request_response.read()),
            FakeGRequestResponse(200, release_file_content.read()),
        ]

        download_release_from_pypi(request.registry.settings, 'pyramid', '1.5')

        self.assertEqual(request_mock.call_count, 4)

        self.assertIn('pyramid', self.root)
        self.assertIn('1.5', self.root['pyramid'].releases)
        self.assertIn('pyramid-1.5.tar.gz', self.root['pyramid']['1.5'].release_files)
        release_file = self.root['pyramid']['1.5']['pyramid-1.5.tar.gz']
        self.assertEqual(release_file.md5_digest, "8747658dcbab709a9c491e43d3b0d58b")
        self.assertEqual(release_file.filename, "pyramid-1.5.tar.gz")
        self.assertEqual(release_file.size, 2413504)
        self.assertEqual(list(self.root['pyramid'].releases.keys()), ['1.5', ])
        assert self.root['pyramid']['1.5'].metadata is not None
        assert self.root['pyramid'].__parent__ is self.root
        assert self.root['pyramid']['1.5'].__parent__ is self.root['pyramid']
        assert self.root['pyramid']['1.5']['pyramid-1.5.tar.gz'].__parent__ is self.root['pyramid']['1.5']
        assert len(list(self.root['pyramid'])) == 1

    @patch('requests.get')
    @patch('papaye.tasks.download.get_connection')
    def test_download_release_from_pypi_with_bad_md5(self, get_connection_mock, request_mock):
        from papaye.factories import repository_root_factory
        from papaye.tasks.download import download_release_from_pypi
        request = get_current_request()
        get_connection_mock.return_value = self.conn

        json_response = open(get_resource('pyramid.json'), 'rb')
        json_request_response = open(get_resource('pyramid1.4.json'), 'rb')
        release_file_content = io.BytesIO(b'corrupted_file')
        request_mock.side_effect = [
            FakeGRequestResponse(200, b'', 'http://pypi.python.org/simple/pyramid/'),
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, json_request_response.read()),
            FakeGRequestResponse(200, release_file_content.read()),
        ]
        root = repository_root_factory(self.conn)

        download_release_from_pypi(request.registry.settings, 'pyramid', '1.5')
        self.assertEqual(request_mock.call_count, 4)

        assert 'pyramid' not in root

    @patch('requests.get')
    @patch('papaye.tasks.download.get_connection')
    def test_download_release_from_pypi_with_existing_package(self, get_connection_mock, request_mock):
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        from papaye.tasks.download import download_release_from_pypi
        request = get_current_request()
        get_connection_mock.return_value = self.conn
        json_response = open(get_resource('pyramid.json'), 'rb')
        json_request_response = open(get_resource('pyramid1.4.json'), 'rb')
        release_file_content = open(get_resource('pyramid-1.5.tar.gz'), 'rb')
        request_mock.side_effect = [
            FakeGRequestResponse(200, b'', 'http://pypi.python.org/simple/pyramid/'),
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, json_request_response.read()),
            FakeGRequestResponse(200, release_file_content.read()),
        ]
        root = repository_root_factory(self.conn)
        package = Package('pyramid')
        release = Release('1.0', '1.0', metadata={})
        release_file = ReleaseFile('pyramid-1.0.tar.gz', b'')
        root['pyramid'] = package
        root['pyramid']['1.0'] = release
        root['pyramid']['1.0']['pyramid-1.0.tar.gz'] = release_file

        download_release_from_pypi(request.registry.settings, 'pyramid', '1.5')

        assert request_mock.call_count == 4
        assert len(list(root['pyramid'])) == 2

    @patch('hashlib.md5')
    @patch('requests.get')
    @patch('papaye.tasks.download.get_connection')
    def test_download_release_from_pypi_different_metadata(self, get_connection_mock, request_mock, md5mock):
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        from papaye.tasks.download import download_release_from_pypi
        request = get_current_request()
        get_connection_mock.return_value = self.conn

        class FakeHexdigestMethod(object):

            def __init__(self, *args, **kwargs):
                pass

            def hexdigest(self):
                return 'd72b664cf3852570faa44a81eb0e448b'

        md5mock.return_value = FakeHexdigestMethod()
        json_response = open(get_resource('pyramid.json'), 'rb')
        json_request_response = open(get_resource('pyramid1.4.json'), 'rb')
        release_file_content = open(get_resource('pyramid-1.5.tar.gz'), 'rb')
        request_mock.side_effect = [
            FakeGRequestResponse(200, b'', 'http://pypi.python.org/simple/pyramid/'),
            FakeGRequestResponse(200, json_response.read()),
            FakeGRequestResponse(200, json_request_response.read()),
            FakeGRequestResponse(200, release_file_content.read()),
        ]
        root = repository_root_factory(self.conn)
        package = Package('pyramid')
        release = Release('1.5', '1.5', metadata={'version': '1.5'}, deserialize_metadata=True)
        release_file = ReleaseFile('pyramid-1.5.tar.gz', b'')
        root['pyramid'] = package
        root['pyramid']['1.5'] = release
        root['pyramid']['1.5']['pyramid-1.5.tar.gz'] = release_file

        download_release_from_pypi(request.registry.settings, 'pyramid', '1.4')

        assert request_mock.call_count == 4
        assert md5mock.call_count == 1
        assert len(list(root['pyramid'])) == 2
        assert '1.4' == root['pyramid']['1.4'].metadata['version']
        existing_version = root['pyramid']['1.5'].metadata['version']
        assert existing_version != root['pyramid']['1.4'].metadata['version']
