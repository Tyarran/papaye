from pyramid_zodbconn import get_connection
from pyramid.request import Request
from pyramid.testing import DummyRequest

from pyramid.security import Allow, Everyone


APP_NAME = __import__(__name__).__name__
APP_ROOT_NAME = '{}_root'.format(APP_NAME)


def user_root_factory(request_or_connection):
    if isinstance(request_or_connection, (Request, DummyRequest)):
        conn = get_connection(request_or_connection)
    else:
        conn = request_or_connection
    zodb_root = conn.root()
    if not '{}_root'.format(APP_NAME) in zodb_root:
        return None
    return zodb_root[APP_ROOT_NAME]['user']


def repository_root_factory(request_or_connection):
    if isinstance(request_or_connection, (Request, DummyRequest)):
        conn = get_connection(request_or_connection)
    else:
        conn = request_or_connection
    zodb_root = conn.root()
    if not '{}_root'.format(APP_NAME) in zodb_root:
        return None
    return zodb_root[APP_ROOT_NAME]['repository']


def evolve_root_factory(request_or_connection):
    if isinstance(request_or_connection, (Request, DummyRequest)):
        conn = get_connection(request_or_connection)
    else:
        conn = request_or_connection
    zodb_root = conn.root()
    return zodb_root['repoze.evolution']


def default_root_factory(request_or_connection):
    if isinstance(request_or_connection, (Request, DummyRequest)):
        conn = get_connection(request_or_connection)
    else:
        conn = request_or_connection
    zodb_root = conn.root()
    return zodb_root


def application_factory(request):
    from papaye.models import Application
    return Application()
