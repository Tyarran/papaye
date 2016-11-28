import importlib
import sys
import transaction

from pkg_resources import EntryPoint
from repoze.evolution.interfaces import IEvolutionManager
from termcolor import colored
from zope.interface import implementer

from papaye.factories import APP_ROOT_NAME


def cleanup():
    del(sys.modules['papaye.app_models'])
    del(sys.modules['papaye.models'])
    sys.modules['papaye.models'] = importlib.import_module('papaye.models')


def load_model(model_name):
    def decorated(func):
        func.load_model = importlib.import_module(model_name)
        return func
    return decorated


def out_model(model_name):
    model = importlib.import_module(model_name)

    def wrapper(func):
        def wrapped(root):
            result = func(root, model)
            return result
        return wrapped
    return wrapper


def context_from_root(root):
    return root[APP_ROOT_NAME]


def error(msg):
    """Format the error message and exit"""
    if isinstance(msg, BaseException):
        msg = str(msg)
    print(colored('ERROR: ', 'red', attrs=('bold', )) + msg)
    sys.exit(1)


class EvolveError(BaseException):
    pass


@implementer(IEvolutionManager)
class PapayeEvolutionManager(object):

    key = 'repoze.evolution'

    def __init__(self, config, evolve_packagename, sw_version, initial_db_version=None):
        self.config = config
        self.package_name = evolve_packagename
        self.sw_version = sw_version
        self.initial_db_version = initial_db_version
        self.last_evolve_model = None

    def _get_root(self, version=None, old_model_module=None):
        if version and old_model_module:
            sys.modules['papaye.app_models'] = sys.modules['papaye.models']
            sys.modules['papaye.models'] = old_model_module
        root = self.config.registry._zodb_databases[''].open().root()
        return root

    def get_sw_version(self):
        return self.sw_version

    def get_db_version(self):
        root = self._get_root()
        registry = root.setdefault(self.key, {})
        db_version = registry.get(self.package_name)
        return self.initial_db_version if db_version is None else db_version

    def set_db_version(self, root, version):
        registry = root.setdefault(self.key, {})
        registry[self.package_name] = version
        root[self.key] = registry

    def evolve_to(self, version):
        scriptname = '%s.evolve%s' % (self.package_name, version)
        evmodule = EntryPoint.parse('x=%s' % scriptname).load(False)
        self.step(version, evmodule)
        self.information('Documentation', evmodule.__doc__ if evmodule.__doc__ is not None else 'UNKNOWN')
        with transaction.manager:
            has_load_model = hasattr(evmodule.evolve, 'load_model')
            if has_load_model:
                root = self._get_root(version, evmodule.evolve.load_model)
                self.last_evolve_model = evmodule.evolve.load_model
                self.information('Load model', self.last_evolve_model.__name__)
            else:
                root = self._get_root(version)
            self.task('Executing script')
            try:
                evmodule.evolve(root, config=self.config)
                if has_load_model:
                    cleanup()
                    self.task('Cleanup model snapshot')
                self.set_db_version(root, version)
            except EvolveError as exc:
                error(exc)

    def task(self, string):
        print('>>> {}'.format(string))

    def step(self, version, evmodule):
        current_version_str = colored(str(version - 1), 'yellow', attrs=('bold', ))
        version_str = colored(str(version), 'yellow', attrs=('bold', ))
        script_str = colored(evmodule.__name__, 'green', attrs=('bold', ))
        print('\n>>> Evolving ({} => {}) {}'.format(current_version_str, version_str, script_str))

    def information(self, title, string):
        print('\t{} {}:\t {}'.format(colored('*', 'green', attrs=('bold',)), title, string))

    def evolve_to_current(self):
        if self.last_evolve_model:
            last_evolve_model_str = colored(str(self.last_evolve_model.__name__), 'yellow', attrs=('bold', ))
            current_model_str = colored('papaye.models', 'yellow', attrs=('bold', ))
            self.task('Evolving {} to current model {}'.format(last_evolve_model_str, current_model_str))
            sys.modules[self.last_evolve_model.__name__] = sys.modules['papaye.models']
            with transaction.manager:
                root = self._get_root()
                root['papaye_root'] = root['papaye_root']
                root['papaye_root']['repository'] = root['papaye_root']['repository']
                root['papaye_root']['user'] = root['papaye_root']['user']
                for package in root[APP_ROOT_NAME]['repository']:
                    root[APP_ROOT_NAME]['repository'][package.__name__] = package
                    for release in package:
                        package[release.__name__] = release
                        for release_file in release:
                            release[release_file.__name__] = release_file
                for user in root[APP_ROOT_NAME]['user']:
                    root[APP_ROOT_NAME]['user'][user.username] = user
