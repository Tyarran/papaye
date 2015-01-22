import json
import unittest

from mock import patch
from pyramid import testing
from requests.exceptions import ConnectionError

from papaye.tests.tools import (
    FakeGRequestResponse,
    disable_cache,
    mock_proxy_response,
    remove_blob_dir,
    set_database_connection,
)


class ProxyTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.blob_dir = set_database_connection(self.request)
        settings = disable_cache()
        self.config = testing.setUp(request=self.request, settings=settings)

    def tearDown(self):
        remove_blob_dir(self.blob_dir)

    @patch('requests.get')
    def test_get_remote_informations(self, mock):
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy()
        result = proxy.get_remote_informations(url)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['info']['name'], 'pyramid')

    @patch('requests.get')
    def test_get_remote_informations_404(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy()
        result = proxy.get_remote_informations(url)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_remote_informations_connection_error(self, mock):
        from papaye.proxy import PyPiProxy
        mock.side_effect = ConnectionError
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy()
        result = proxy.get_remote_informations(url)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_remote_package_name(self, mock):
        from papaye.proxy import PyPiProxy
        mock.side_effect = ConnectionError
        url = "http://pypi.python.org/pypi/pyramid/json"

        proxy = PyPiProxy()
        result = proxy.get_remote_package_name(url)
        self.assertIsNone(result)

    def test_smart_merge_with_other_release(self):
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')
        package1['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package1['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        package2 = Package(name='pyramid')
        package2['1.6'] = Release(name='1.6', version='1.6', metadata={})
        package2['1.6']['pyramid-1.6.tar.gz'] = ReleaseFile(
            filename='pyramid-1.6.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        result = smart_merge(package1, package2)

        assert isinstance(result, Package)
        assert len(list(result.__parent__)) == 1
        assert len(list(result)) == 2
        assert repository_root_factory(self.request) is not result.__parent__

        result = smart_merge(package1, package2)

        assert isinstance(result, Package)
        assert len(list(result)) == 2
        assert repository_root_factory(self.request) is not result.__parent__

    def test_smart_merge_with_other_package(self):
        from papaye.models import Package, Release, ReleaseFile
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')
        package1['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package1['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        package2 = Package(name='other')
        package2['1.6'] = Release(name='1.6', version='1.6', metadata={})
        package2['1.6']['other-1.6.tar.gz'] = ReleaseFile(
            filename='other-1.6.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        result = smart_merge(package1, package2)

        assert isinstance(result, Package)
        assert len(list(result.__parent__)) == 1
        assert result.__name__ == 'pyramid'

    def test_smart_merge_with_different_release_file(self):
        from papaye.factories import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')
        package1['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package1['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'',
            md5_digest='12345'
        )

        package2 = Package(name='pyramid')
        package2['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package2['1.5']['pyramid-1.5.whl'] = ReleaseFile(
            filename='pyramid-1.5.whl',
            content=b'',
            md5_digest='12345'
        )

        result = smart_merge(package1, package2)

        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 2
        assert repository_root_factory(self.request) is not result.__parent__

    def test_smart_merge_with_new_package(self):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')

        package2 = Package(name='pyramid')
        package2['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package2['1.5']['pyramid-1.5.whl'] = ReleaseFile(
            filename='pyramid-1.5.whl',
            content=b'',
            md5_digest='12345'
        )
        root = Root()

        result = smart_merge(package1, package2, root=root)

        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 1
        assert result.__parent__ is root

    def test_smart_merge_with_none_remote_package(self):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import smart_merge
        package = Package(name='pyramid')
        package['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package['1.5']['pyramid-1.5.whl'] = ReleaseFile(
            filename='pyramid-1.5.whl',
            content=b'',
            md5_digest='12345'
        )
        root = Root()

        result = smart_merge(package, None, root=root)

        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 1
        assert result.__parent__ is root

    def test_smart_merge_dont_update_existing_release_file(self):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')
        package1['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package1['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )

        package2 = Package(name='pyramid')
        package2['1.5'] = Release(name='1.5', version='1.5', metadata={})
        package2['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'a new content',
            md5_digest='12345'
        )
        root = Root()

        import pdb; pdb.set_trace()
        result = smart_merge(package1, package2, root=root)


        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 1
        assert result['1.5']['pyramid-1.5.tar.gz'].content.open().read() == b'a existing content'
        assert result.__parent__ is root

    @patch('requests.get')
    def test_build_remote_repository(self, mock):
        from papaye.models import Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        proxy = PyPiProxy()

        result = proxy.build_remote_repository('pyramid')

        assert isinstance(result, Root)
        assert 'pyramid' in list(result.keys())
        assert len(list(result['pyramid'])) == 81
        assert not hasattr(list(result['pyramid'])[0], 'metadata')

    @patch('requests.get')
    def test_build_remote_repository_with_metadata(self, mock):
        from papaye.models import Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        proxy = PyPiProxy()

        result = proxy.build_remote_repository('pyramid', metadata=True)

        assert isinstance(result, Root)
        assert 'pyramid' in list(result.keys())
        assert len(list(result['pyramid'])) == 81
        assert hasattr(list(result['pyramid'])[0], 'metadata')
        assert len(list(result['pyramid'])[0].metadata.keys()) == 13

    @patch('requests.get')
    def test_build_remote_repository_with_release_name(self, mock):
        from papaye.models import Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        proxy = PyPiProxy()

        result = proxy.build_remote_repository('pyramid', release_name='1.5')

        assert isinstance(result, Root)
        assert 'pyramid' in list(result.keys())
        assert len(list(result['pyramid'])) == 1

    @patch('requests.get')
    def test_build_remote_repository_with_unknown_package(self, mock):
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')
        proxy = PyPiProxy()

        result = proxy.build_remote_repository('pyramid', metadata=True)

        assert result is None

    @patch('requests.get')
    def test_merged_repository(self, mock):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        package1 = Package(name='pyramid')
        package1['100.5'] = Release(name='100.5', version='100.5', metadata={})
        package1['100.5']['pyramid-100.5.tar.gz'] = ReleaseFile(
            filename='pyramid-100.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        proxy = PyPiProxy()
        result = proxy.merged_repository(package1)

        assert isinstance(result, Root)
        assert [pack.__name__ for pack in result] == ["pyramid", ]
        assert len(list(result['pyramid'])) == 82
        assert '100.5' in [rel for rel in result['pyramid'].releases]
        assert not hasattr(result['pyramid']['1.5'], 'metadata')

    @patch('requests.get')
    def test_merged_repository_with_metadata(self, mock):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        package1 = Package(name='pyramid')
        package1['100.5'] = Release(name='100.5', version='100.5', metadata={})
        package1['100.5']['pyramid-100.5.tar.gz'] = ReleaseFile(
            filename='pyramid-100.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        proxy = PyPiProxy()
        result = proxy.merged_repository(package1, metadata=True)

        assert isinstance(result, Root)
        assert [pack.__name__ for pack in result] == ["pyramid", ]
        assert len(list(result['pyramid'])) == 82
        assert '100.5' in [rel for rel in result['pyramid'].releases]
        assert hasattr(result['pyramid']['1.5'], 'metadata')

    @patch('requests.get')
    def test_merged_repository_with_release_name(self, mock):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        package1 = Package(name='pyramid')
        package1['100.5'] = Release(name='100.5', version='100.5', metadata={})
        package1['100.5']['pyramid-100.5.tar.gz'] = ReleaseFile(
            filename='pyramid-100.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        proxy = PyPiProxy()
        result = proxy.merged_repository(package1, release_name='1.5')

        assert isinstance(result, Root)
        assert [pack.__name__ for pack in result] == ["pyramid", ]
        assert len(list(result['pyramid'])) == 2
        assert '1.5' in result['pyramid'].releases.keys()
        assert '100.5' in [rel for rel in result['pyramid'].releases]

    @patch('requests.get')
    def test_merged_repository_without_repository_package(self, mock):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')
        package1 = Package(name='pyramid')
        package1['100.5'] = Release(name='100.5', version='100.5', metadata={})
        package1['100.5']['pyramid-100.5.tar.gz'] = ReleaseFile(
            filename='pyramid-100.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        proxy = PyPiProxy()
        result = proxy.merged_repository(package1, metadata=True)

        assert isinstance(result, Root)
        assert [pack.__name__ for pack in result] == ["pyramid", ]
        assert len(list(result['pyramid'])) == 1
