from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver

from papaye.factories.root import (
    repository_root_factory,
    user_root_factory,
)
from papaye.tasks.devices import DummyScheduler
from papaye.tasks import TaskRegistry


def start_scheduler(config):
    reader = config.settings_reader()
    settings = reader.settings
    scheduler = reader.read_str('papaye.scheduler')
    scheduler_keys = (key[17:] for key in settings.keys()
                      if key.startswith('papaye.scheduler.'))
    if not reader.read_bool('papaye.cache') or scheduler is None:
        scheduler = DummyScheduler()
    else:
        resolver = DottedNameResolver()
        scheduler_kwargs = {key[17:]: val for key, val in settings.items()
                            if key in scheduler_keys}
        scheduler = resolver.maybe_resolve(scheduler)(**scheduler_kwargs)
    scheduler.start()
    TaskRegistry().register_scheduler(scheduler)

    def get_scheduler(request):

        return scheduler

    config.add_request_method(
        get_scheduler,
        'scheduler',
        property=True,
        reify=True
    )


def check_database_config(config):
    from papaye.models import get_manager
    manager = get_manager(config)
    if manager.get_db_version() < manager.get_sw_version():
        raise ConfigurationError(
            'Your database need to be updated! Run '
            '"papaye_evolve path_to_your_config_file.ini" command first'
        )
    conn = config.registry._zodb_databases[''].open()
    if user_root_factory(conn) is None \
            or repository_root_factory(conn) is None:
        raise ConfigurationError('Database does not exist! Run "papaye_init '
                                 'path_to_your_config_file.ini command first')
    return True


def includeme(config):
    reader = config.settings_reader()
    check_database_config(config)
    config.scan(ignore='papaye.tests')
    if not reader.read_bool('papaye.worker.combined'):
        start_scheduler(config)
