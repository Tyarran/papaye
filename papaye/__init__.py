from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings

from papaye.authentification import RouteNameAuthPolicy
from papaye.bundles import papaye_css_assets,  papaye_js_assets, require_js_resources
from papaye.factories import (
    repository_root_factory,
    user_root_factory,
    application_factory,
)
from papaye.models import User
from papaye.tasks.devices import DummyScheduler
from papaye.tasks import TaskRegistry


logger = logging.getLogger(__name__)
WEBASSETS_DEFAULT_CONFIG = {
    "debug": False,
    "updater": 'timestamp',
    "cache": True,
    "url_expire": False,
    "static_view": True,
    "cache_max_age": 3600,
}
random_passphrase = lambda: ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
my_session_factory = SignedCookieSessionFactory(random_passphrase())


def auth_check_func(username, password, request):
    user = User.by_username(username, request)
    if user and user.password_verify(password):
        return user.groups
    return None


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
    settings = config.registry.settings
    if settings.get('papaye.cache').lower() != 'true' or settings.get('papaye.scheduler') is None:
        scheduler = DummyScheduler()
    else:
        resolver = DottedNameResolver()
        scheduler_kwargs = {key[17:]: value for key, value in config.registry.settings.items()
                            if key.startswith('papaye.scheduler.')}
        scheduler = resolver.maybe_resolve(config.registry.settings.get('papaye.scheduler'))(**scheduler_kwargs)
    scheduler.start()
    TaskRegistry().register_scheduler(scheduler)

    def get_scheduler(request):

        return scheduler

    config.add_request_method(get_scheduler, 'scheduler', property=True, reify=True)


def configure_routes(config):
    # config.add_route('islogged', '/islogged', factory=index_root_factory)
    config.add_route('login', '/login/', factory=user_root_factory)
    config.add_route('logout', '/logout')
    config.add_route('home', '/', factory=application_factory)
    config.add_route('simple', '/simple*traverse', factory=repository_root_factory)


def configure_views(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_notfound_view(notfound, append_slash=True)


def configure_authn_and_authz(config):
    authn_policy = RouteNameAuthPolicy(
        default=AuthTktAuthenticationPolicy(random_passphrase(), hashalg='sha512'),
        simple=BasicAuthAuthenticationPolicy(check=auth_check_func),
    )
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    settings = config.registry.settings
    if settings.get('papaye.open_repository', 'False') == 'False':
        config.set_default_permission('view')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    add_directives(config)
    configure_authn_and_authz(config)
    config.set_session_factory(my_session_factory)

    configure_views(config)  # Views
    configure_routes(config)  # Routes
    config.commit()
    config.add_tween('papaye.tweens.LoginRequiredTweenFactory')
    config.scan(ignore='papaye.tests')
    if 'papaye.worker.combined' not in settings or bool(settings['papaye.worker.combined']):
        config.start_scheduler()

    config.add_tween('papaye.tweens.LoginRequiredTweenFactory')
    return config.make_wsgi_app()
