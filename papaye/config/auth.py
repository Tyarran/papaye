from random import choice

from pyramid.authentication import (
    BasicAuthAuthenticationPolicy, AuthTktAuthenticationPolicy
)
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory

from papaye.authentification import RouteNameAuthPolicy
from papaye.models import User


CHOICES = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&(-_=+)'


def random_passphrase():
    return ''.join([choice(CHOICES) for i in range(50)])


def auth_check_func(username, password, request):
    user = User.by_username(username, request)
    if user and user.password_verify(password):
        return user.groups
    return None


def includeme(config):
    session_factory = SignedCookieSessionFactory(random_passphrase())
    authn_policy = RouteNameAuthPolicy(
        default=AuthTktAuthenticationPolicy(
            random_passphrase(), hashalg='sha512'
        ),
        simple=BasicAuthAuthenticationPolicy(check=auth_check_func),
    )
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    settings = config.registry.settings
    if settings.get('papaye.anonymous_browse', 'False') == 'False':
        config.set_default_permission('view')
    config.set_session_factory(session_factory)
