import hashlib
import os

from CodernityDB.database import Database, RecordNotFound
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator, ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow
from pyramid.threadlocal import get_current_registry
from pyramid_beaker import set_cache_regions_from_settings

from papaye.tasks.devices import get_producer, start_queue, start_collector


def check_func(*args, **kwargs):
    login, password, request = args
    try:
        user = request.db.get('user', login, with_doc=True)
        if user['doc']['password'] == hashlib.sha256(password).digest():
            return [login, ]
    except RecordNotFound:
        pass
    return None


authn_policy = BasicAuthAuthenticationPolicy(check=check_func)
authz_policy = ACLAuthorizationPolicy()


def test_db_configuration(settings):
    url = settings.get('codernity.url', None)
    if not url:
        raise ConfigurationError('No codernity.url option in INI file')
    database_path = url[7:]
    db = Database(database_path)
    if not db.exists():
        raise ConfigurationError('Database does not exist! Run "papaye_init" script first')
    return True


def get_db(settings):
    database_path = settings['codernity.url'][7:]
    db = Database(database_path)
    db.open()
    return db


class RootFactory(object):
    """
    Pyramid root factory that contains the ACL.
    """
    root = None

    class Root(object):
        __acl__ = None

    def __call__(self, request):
        if self.root is None:
            db = request.db
            credentials = self.get_user_acl_from_database(db)
            self.root = self.Root()
            self.root.__acl__ = credentials
        return self.root

    def get_user_acl_from_database(self, db):
        credentials = []
        for group in db.all('group', with_doc=True):
            credentials.append((Allow, group['doc']['name'], group['doc']['permissions']))
        return credentials


def notfound(request):
    return HTTPNotFound('Not found.')


def registrer_producer(settings):
    global_registry = get_current_registry()
    global_registry.producer = get_producer(settings)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    repository = settings.get('papaye.repository', None)
    if not repository:
        raise ConfigurationError('Variable {} missing in settings'.format('papaye.repository'))
    elif not os.path.exists(repository):
        os.makedirs(repository)
    test_db_configuration(settings)
    add_db = lambda request: get_db(settings)
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings, root_factory=RootFactory())
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('repository', 'repository')
    config.add_route('simple', '/simple/')
    config.add_route('simple_release', '/simple/{package}/')
    config.add_route('download_release', '/simple/{package}/{release}')
    config.add_notfound_view(notfound, append_slash=True)
    config.add_request_method(add_db, 'db', reify=True)
    start_queue(settings)
    start_collector(settings)
    registrer_producer(settings)
    config.scan()
    return config.make_wsgi_app()
