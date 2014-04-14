from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid_beaker import set_cache_regions_from_settings

from papaye.factories import repository_root_factory
from papaye.models import User


APP_NAME = __name__
__version__ = '0.1'

# from papaye.tasks.devices import get_producer, start_queue, start_collector


def auth_check_func(username, password, request):
    user = User.by_username(username, request)
    if user and user.password_verify(password):
        return user.groups
    return None


def notfound(request):
    return HTTPNotFound()


# def registrer_producer(settings):
#     global_registry = get_current_registry()
#     global_registry.producer = get_producer(settings)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    authn_policy = BasicAuthAuthenticationPolicy(check=auth_check_func)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('simple', '/simple*traverse', factory=repository_root_factory)
    config.add_notfound_view(notfound, append_slash=True)
    # start_queue(settings)
    # start_collector(settings)
    # registrer_producer(settings)
    config.scan()
    return config.make_wsgi_app()
