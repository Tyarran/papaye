import unittest

from mock import patch
from pyramid.threadlocal import get_current_request
from requests.exceptions import ConnectionError

from papaye.factories import models as factories
from papaye.tests.tools import FakeGRequestResponse
from papaye.tests.tools import mock_proxy_response


class ProxyTest(unittest.TestCase):

    def setUp(self):
        self.request = get_current_request()

    @patch('requests.get')
    def test_get_remote_informations(self, mock):
        # Given
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        url = "http://pypi.python.org/pypi/pyramid/json"
        proxy = PyPiProxy()

        # When
        result = proxy.get_remote_informations(url)

        # Then
        self.assertIsInstance(result, dict)
        self.assertEqual(result['info']['name'], 'pyramid')

    @patch('requests.get')
    def test_get_remote_informations_404(self, mock):
        # Given
        from papaye.proxy import PyPiProxy
        mock.return_value = FakeGRequestResponse(404, b'')
        url = "http://pypi.python.org/pypi/pyramid/json"
        proxy = PyPiProxy()

        # When
        result = proxy.get_remote_informations(url)

        # Then
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_remote_informations_connection_error(self, mock):
        # Given
        from papaye.proxy import PyPiProxy
        mock.side_effect = ConnectionError
        url = "http://pypi.python.org/pypi/pyramid/json"
        proxy = PyPiProxy()

        # When
        result = proxy.get_remote_informations(url)

        # Then
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_remote_package_name(self, mock):
        # Given
        from papaye.proxy import PyPiProxy
        mock.side_effect = ConnectionError
        url = "http://pypi.python.org/pypi/pyramid/json"
        proxy = PyPiProxy()

        # When
        result = proxy.get_remote_package_name(url)

        # Then
        self.assertIsNone(result)

    def test_smart_merge_with_other_release(self):
        # Given
        from papaye.factories.root import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        from papaye.proxy import smart_merge
        release1 = factories.ReleaseFactory(
            version='1.5',
            filename='pyramid-1.5.tar.gz',
            md5_digest='12345',
            package__name='pyramid',
        )
        release2 = factories.ReleaseFactory(
            version='1.6',
            filename='pyramid-1.6.tar.gz',
            md5_digest='12345',
            package__name='pyramid',
        )
        package1 = release1.package
        package2 = release2.package

        # When
        result = smart_merge(package1, package2)

        # Then
        assert isinstance(result, Package)
        assert len(list(result.root)) == 1
        assert len(list(result)) == 2
        assert repository_root_factory(self.request) is not result.root
        result = smart_merge(package1, package2)
        assert isinstance(result, Package)
        assert len(list(result)) == 2
        assert repository_root_factory(self.request) is not result.root

    def test_smart_merge_with_other_package(self):
        from papaye.models import Package, Release, ReleaseFile
        from papaye.proxy import smart_merge
        release1 = factories.ReleaseFactory(
            version='1.5',
            filename='pyramid-1.5.tar.gz',
            md5_digest='12345',
            package__name='pyramid',
        )
        release2 = factories.ReleaseFactory(
            version='1.6',
            filename='pyramid-1.6.tar.gz',
            md5_digest='12345',
            package__name='pyramid',
        )
        package1 = release1.package
        package2 = release2.package

        result = smart_merge(package1, package2)

        assert isinstance(result, Package)
        assert len(list(result.root)) == 1
        assert result.__name__ == 'pyramid'

    def test_smart_merge_with_different_release_file(self):
        # Given
        from papaye.factories.root import repository_root_factory
        from papaye.models import Package, Release, ReleaseFile
        from papaye.proxy import smart_merge
        release_file1 = factories.ReleaseFileFactory(
            release__version='1.5',
            filename='pyramid-1.5.tar.gz',
            md5_digest='12345',
            release__package__name='pyramid',
        )
        release_file2 = factories.ReleaseFileFactory(
            release__version='1.5',
            filename='pyramid-1.5.whl',
            md5_digest='12345',
            release__package__name='pyramid',
        )
        package1 = release_file1.release.package
        package2 = release_file2.release.package

        # When
        result = smart_merge(package1, package2)

        # Then
        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 2
        assert repository_root_factory(self.request) is not result.root

    def test_smart_merge_with_new_package(self):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')

        package2 = Package(name='pyramid')
        package2['1.5'] = Release(version='1.5', metadata={})
        package2['1.5']['pyramid-1.5.whl'] = ReleaseFile(
            filename='pyramid-1.5.whl',
            content=b'',
            md5_digest='12345'
        )
        root = Root(name='root')

        result = smart_merge(package1, package2, root=root)

        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 1
        assert result.__parent__ is root

    def test_smart_merge_with_none_remote_package(self):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import smart_merge
        package = Package(name='pyramid')
        package['1.5'] = Release(version='1.5', metadata={})
        package['1.5']['pyramid-1.5.whl'] = ReleaseFile(
            filename='pyramid-1.5.whl',
            content=b'',
            md5_digest='12345'
        )
        root = Root(name='root')

        result = smart_merge(package, None, root=root)

        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 1
        assert result.__parent__ is root

    def test_smart_merge_dont_update_existing_release_file(self):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import smart_merge
        package1 = Package(name='pyramid')
        package1['1.5'] = Release(version='1.5', metadata={})
        package1['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )

        package2 = Package(name='pyramid')
        package2['1.5'] = Release(version='1.5', metadata={})
        package2['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'a new content',
            md5_digest='12345'
        )
        root = Root(name='root')

        result = smart_merge(package1, package2, root=root)

        assert isinstance(result, Package)
        assert len(list(result)) == 1
        assert len(list(result['1.5'])) == 1
        assert result.__parent__ is root

    @patch('requests.get')
    def test_build_remote_repository(self, mock):
        from papaye.models import Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        proxy = PyPiProxy()

        result = proxy.build_remote_repository('pyramid')

        assert isinstance(result, Root)
        assert 'pyramid' in [e.__name__ for e in result]
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
        package1['100.5'] = Release(version='100.5', metadata={})
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
        for release in result['pyramid']:
            for release_file in release:
                assert hasattr(release_file, 'md5_digest')

    @patch('requests.get')
    def test_merged_repository_with_metadata(self, mock):
        from papaye.models import Package, Release, ReleaseFile, Root
        from papaye.proxy import PyPiProxy
        mock_proxy_response(mock)
        package1 = Package(name='pyramid')
        package1['100.5'] = Release(version='100.5', metadata={})
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
        package1['100.5'] = Release(version='100.5', metadata={})
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
        package1['100.5'] = Release(version='100.5', metadata={})
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

    def test_clone(self):
        from papaye.proxy import clone
        from papaye.models import Package, Release, ReleaseFile
        package = Package(name='pyramid')
        package['1.5'] = Release(version='1.5', metadata={})
        package['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )

        result = clone(package)

        assert result is not None
        assert result is not package
        assert result.__name__ == package.__name__
        assert '1.5' in list(result.releases.keys())
        assert result['1.5'] is not package['1.5']

    def test_clone_complexe(self):
        from papaye.proxy import clone
        from papaye.models import Package, Release, ReleaseFile
        package = Package(name='pyramid')
        package['1.3'] = Release(version='1.3', metadata={})
        package['1.4'] = Release(version='1.4', metadata={})
        package['1.5'] = Release(version='1.5', metadata={})
        package['1.3']['pyramid-1.3.tar.gz'] = ReleaseFile(
            filename='pyramid-1.3.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        package['1.4']['pyramid-1.4.tar.gz'] = ReleaseFile(
            filename='pyramid-1.4.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        package['1.5']['pyramid-1.5.tar.gz'] = ReleaseFile(
            filename='pyramid-1.5.tar.gz',
            content=b'a existing content',
            md5_digest='12345'
        )
        package['1.5']['pyramid-1.5.whl'] = ReleaseFile(
            filename='pyramid-1.5.whl',
            content=b'a existing content',
            md5_digest='12345'
        )

        result = clone(package)

        assert result is not None
        assert result is not package
        assert ['1.3', '1.4', '1.5'] == list(result.releases.keys())
        for release_name in ['1.3', '1.4', '1.5']:
            assert result[release_name] != package[release_name]

        assert 'pyramid-1.3.tar.gz' in list(result['1.3'].release_files.keys())
        release_file = result['1.3']['pyramid-1.3.tar.gz']
        assert release_file is not package['1.3']['pyramid-1.3.tar.gz']
        assert release_file.path == package['1.3']['pyramid-1.3.tar.gz'].path
        assert release_file.md5_digest == package['1.3']['pyramid-1.3.tar.gz'].md5_digest
        assert release_file.size == package['1.3']['pyramid-1.3.tar.gz'].size

        release_file = result['1.4']['pyramid-1.4.tar.gz']
        assert release_file is not package['1.4']['pyramid-1.4.tar.gz']
        assert release_file.path == package['1.4']['pyramid-1.4.tar.gz'].path
        assert release_file.md5_digest == package['1.4']['pyramid-1.4.tar.gz'].md5_digest
        assert release_file.size == package['1.4']['pyramid-1.4.tar.gz'].size

        release_file = result['1.5']['pyramid-1.5.tar.gz']
        assert release_file is not package['1.5']['pyramid-1.5.tar.gz']
        assert release_file.path == package['1.5']['pyramid-1.5.tar.gz'].path
        assert release_file.md5_digest == package['1.5']['pyramid-1.5.tar.gz'].md5_digest
        assert release_file.size == package['1.5']['pyramid-1.5.tar.gz'].size

        release_file = result['1.5']['pyramid-1.5.whl']
        assert release_file is not package['1.5']['pyramid-1.5.whl']
        assert release_file.path == package['1.5']['pyramid-1.5.whl'].path
        assert release_file.md5_digest == package['1.5']['pyramid-1.5.whl'].md5_digest
        assert release_file.size == package['1.5']['pyramid-1.5.whl'].size
