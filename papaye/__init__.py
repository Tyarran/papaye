import sys

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator, ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
from pyramid_beaker import set_cache_regions_from_settings

from papaye.factories import repository_root_factory, user_root_factory
from papaye.models import User, get_manager, SW_VERSION
from papaye.tasks.devices import Scheduler, Producer
from pyramid.threadlocal import get_current_registry


def auth_check_func(username, password, request):
    user = User.by_username(username, request)
    if user and user.password_verify(password):
        return user.groups
    return None


def check_database_config(settings, config):
    manager = get_manager(config)
    if manager.get_db_version() < SW_VERSION:
        raise ConfigurationError('Your database need to be updated! Run "papaye_evolve path_to_your_config_file.ini" command first')
    conn = config.registry._zodb_databases[''].open()
    if user_root_factory(conn) is None or repository_root_factory(conn) is None:
        raise ConfigurationError('Database does not exist! Run "papaye_init path_to_your_config_file.ini command first')
    return True


def notfound(request):
    return HTTPNotFound()


def add_directives(config):
    config.add_directive('start_scheduler', start_scheduler)


def start_scheduler(config):
    registry = get_current_registry()
    registry.producer = Producer(config)
    if sys.argv[0].endswith('pserve'):
        scheduler = Scheduler(config.registry.settings, config)
        scheduler.run()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    add_directives(config)
    authn_policy = BasicAuthAuthenticationPolicy(check=auth_check_func)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('simple', '/simple*traverse', factory=repository_root_factory)
    config.add_notfound_view(notfound, append_slash=True)
    check_database_config(settings, config)
    config.scan()
    config.start_scheduler()
    return config.make_wsgi_app()
