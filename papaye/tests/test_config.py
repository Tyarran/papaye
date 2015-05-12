import mock
import shutil
import unittest

from mock import patch
from pyramid import testing
from pyramid.config import Configurator
from pyramid.threadlocal import get_current_request
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


class TestScheduler(object):

    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def add_task(self, *args):
        pass

    def task_id(self, task_tuple):
        pass

    def get_task(self):
        pass

    def add_result(self, worker_id, result):
        pass

    def status(self, task_id):
        pass

    def shutdown(self):
        pass


@mock.patch('papaye.tasks.TaskRegistry.register_scheduler')
def test_start_scheduler(mock):
    from papaye import start_scheduler
    config = Configurator()
    config.registry.settings = {
        'papaye.cache': 'true',
        'papaye.scheduler': 'papaye.tests.test_config:TestScheduler',
    }

    start_scheduler(config)

    get_current_request()

    assert isinstance(mock.call_args[0][0], TestScheduler)


@mock.patch('papaye.tasks.TaskRegistry.register_scheduler')
def test_start_scheduler_without_scheduler_in_configuration(mock):
    from papaye import start_scheduler
    from papaye.tasks.devices import DummyScheduler
    config = Configurator()
    config.registry.settings = {
        'papaye.cache': 'true',
    }

    start_scheduler(config)

    get_current_request()

    assert isinstance(mock.call_args[0][0], DummyScheduler)


@mock.patch('papaye.tasks.TaskRegistry.register_scheduler')
def test_start_scheduler_without_cache_in_configuration(mock):
    from papaye import start_scheduler
    from papaye.tasks.devices import DummyScheduler
    config = Configurator()
    config.registry.settings = {
        'papaye.cache': 'true',
    }

    start_scheduler(config)

    get_current_request()

    assert isinstance(mock.call_args[0][0], DummyScheduler)
