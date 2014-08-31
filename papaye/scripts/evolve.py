import sys

from pyramid.paster import get_appsettings
from pyramid.config import Configurator
from repoze.evolution import evolve_to_latest

from papaye.models import get_manager


def main(*argv, **kwargs):
    config_file = sys.argv[-1]
    settings = get_appsettings(config_file)
    config = Configurator(settings=settings)
    manager = get_manager(config)
    if manager.get_db_version() >= manager.get_sw_version():
        sys.stdout.write('Your database is already up do date... ')
    else:
        sys.stdout.write('Your database need to be updated... ')
        evolve_to_latest(manager)
    sys.stdout.write('Done!\n')
