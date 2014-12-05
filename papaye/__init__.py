import sys

from random import choice

from pyramid.authentication import BasicAuthAuthenticationPolicy, AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator, ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.threadlocal import get_current_registry
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.session import SignedCookieSessionFactory

from papaye.bundles import papaye_js, papaye_css, papaye_font
from papaye.factories import repository_root_factory, user_root_factory, index_root_factory
from papaye.models import User
from papaye.tasks.devices import Scheduler, Producer


def auth_check_func(username, password, request):
    user = User.by_username(username, request)
    if user and user.password_verify(password):
        return user.groups
    return None

random_passphrase = lambda: ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

my_session_factory = SignedCookieSessionFactory(random_passphrase())


def check_database_config(config):
    from papaye.models import get_manager
    manager = get_manager(config)
    if manager.get_db_version() < manager.get_sw_version():
        raise ConfigurationError('Your database need to be updated! Run '
                                 '"papaye_evolve path_to_your_config_file.ini" command first')
    conn = config.registry._zodb_databases[''].open()
    if user_root_factory(conn) is None or repository_root_factory(conn) is None:
        raise ConfigurationError('Database does not exist! Run "papaye_init '
                                 'path_to_your_config_file.ini command first')
    return True


def notfound(request):
    return HTTPNotFound()


def add_directives(config):
    config.add_directive('check_database_config', check_database_config)
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
    authn_policy = AuthTktAuthenticationPolicy(random_passphrase(), hashalg='sha512')
    # authn_policy = AuthenticationStackPolicy()
    # authn_policy.add_policy('basic', BasicAuthAuthenticationPolicy(check=auth_check_func))
    # authn_policy.add_policy('tkt', AuthTktAuthenticationPolicy(secret='1234'))
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_session_factory(my_session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('islogged', '/islogged', factory=index_root_factory)
    config.add_route('login', '/login', factory=user_root_factory)
    config.add_route('logout', '/logout')
    config.add_route('browse', '/browse', factory=index_root_factory)
    config.add_route('simple', '/simple*traverse', factory=repository_root_factory)
    config.add_notfound_view(notfound, append_slash=True)
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    assets_env = config.get_webassets_env()
    config.commit()
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.assets_environment = assets_env
    config.add_webasset('papaye_js', papaye_js)
    config.add_webasset('papaye_css', papaye_css)
    config.add_webasset('papaye_font', papaye_font)
    config.check_database_config()
    config.scan()
    config.start_scheduler()
    return config.make_wsgi_app()
