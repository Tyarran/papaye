import shutil
import unittest

from mock import patch
from pyramid import testing
from repoze.evolution import ZODBEvolutionManager

from papaye.tests.tools import set_database_connection


class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.blob_dir = set_database_connection(self.request, config=self.config)

    def tearDown(self):
        shutil.rmtree(self.blob_dir)

    def get_root(self):
        from papaye.models import Root
        root = Root()

        def root_func():
            return {'papaye_root': {'repository': {}, 'user': {}}}

        class P_jar:
            pass
        root._p_jar = P_jar()
        root._p_jar.root = root_func
        return root

    @patch('papaye.models.get_manager')
    def test_check_database_config(self, mock):
        from papaye import check_database_config
        root = self.get_root()
        mock.return_value = ZODBEvolutionManager(
            root,
            evolve_packagename='papaye.evolve',
            sw_version=0,
            initial_db_version=0
        )
        result = check_database_config(self.config)
        self.assertTrue(result)

    @patch('papaye.models.get_manager')
    def test_check_database_config_outdated(self, mock):
        from papaye import check_database_config
        root = self.get_root()
        manager = ZODBEvolutionManager(
            root,
            evolve_packagename='papaye.evolve',
            sw_version=1,
            initial_db_version=0
        )
        manager.sw_version = 1
        mock.return_value = manager

        from pyramid.config import ConfigurationError
        self.assertRaises(ConfigurationError, check_database_config, self.config)

    @patch('papaye.models.get_manager')
    def test_check_database_config_without_approot(self, mock):
        from papaye import check_database_config
        root = self.get_root()
        manager = ZODBEvolutionManager(
            root,
            evolve_packagename='papaye.evolve',
            sw_version=0,
            initial_db_version=0
        )
        mock.return_value = manager

        # Remove app_root
        del(self.config.registry._zodb_databases[''].open().root()['papaye_root'])
        import transaction
        transaction.commit()

        from pyramid.config import ConfigurationError
        self.assertRaises(ConfigurationError, check_database_config, self.config)
