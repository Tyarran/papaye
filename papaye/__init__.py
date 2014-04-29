import sys

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid_beaker import set_cache_regions_from_settings

from papaye.factories import repository_root_factory
from papaye.models import User
from papaye.tasks.devices import Scheduler, Producer
from pyramid.threadlocal import get_current_registry


def auth_check_func(username, password, request):
    user = User.by_username(username, request)
    if user and user.password_verify(password):
        return user.groups
    return None


def notfound(request):
    return HTTPNotFound()


def add_directives(config):
    config.add_directive('start_scheduler', start_scheduler)


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
    config.start_scheduler()
    config.scan()
    return config.make_wsgi_app()


def start_scheduler(config):
    registry = get_current_registry()
    registry.producer = Producer(config.registry.settings)
    if sys.argv[0].endswith('pserve'):
        scheduler = Scheduler(config.registry.settings)
        scheduler.start()


def add_task_sender(config, sender):
    config.registry.producer = sender


def add_queue_device(config, queue):
    config.registry.queue = queue
    config.registry.queue.start()


def add_collector_device(config, collector):
    config.registry.collector = collector
    config.registry.collector.start()
