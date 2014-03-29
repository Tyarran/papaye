#import hashlib
import lmdb
import os
import transaction

#from CodernityDB.database import Database, RecordNotFound
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator, ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
#from pyramid.security import Allow
from pyramid.threadlocal import get_current_registry
from pyramid_beaker import set_cache_regions_from_settings
from pyramid_zodbconn import get_connection
from BTrees.OOBTree import OOBTree
#from persistent.mapping import PersistentMapping

APP_NAME = __name__

#from papaye.tasks.devices import get_producer, start_queue, start_collector


def check_func(*args, **kwargs):
    #login, password, request = args
    #try:
        #user = request.db.get('user', login, with_doc=True)
        #if user['doc']['password'] == hashlib.sha256(password).digest():
            #return [login, ]
    #except RecordNotFound:
        #pass
    return None


authn_policy = BasicAuthAuthenticationPolicy(check=check_func)
authz_policy = ACLAuthorizationPolicy()


def test_db_configuration(settings):
    path = settings.get('database.path', None)
    if not path:
        raise ConfigurationError('No database.path option in INI file')
    return True


def register_db_environment(db_env):
    registry = get_current_registry()
    registry.db_env = db_env


def get_db_environment(settings):
    database_path = settings.get('database.path')
    env = lmdb.open(database_path)
    return env


class RootFactory(object):
    """
    Pyramid root factory that contains the ACL.
    """
    root = None

    class Root(object):
        __acl__ = None

    def __call__(self, request):
        return self.Root()
        #if self.root is None:
            #db = request.db_env
            #credentials = self.get_user_acl_from_database(db)
            #self.root = self.Root()
            #self.root.__acl__ = credentials
        #return self.root

    def get_user_acl_from_database(self, db):
        credentials = []
        #for group in db.all('group', with_doc=True):
            #credentials.append((Allow, group['doc']['name'], group['doc']['permissions']))
        return credentials


def root_factory(request):
    conn = get_connection(request)
    zodb_root = conn.root()
    if not '{}_root'.format(APP_NAME) in zodb_root:
        app_root = OOBTree()
        zodb_root['{}_root'.format(APP_NAME)] = app_root
        transaction.commit()
    return zodb_root['{}_root'.format(APP_NAME)]


def notfound(request):
    return HTTPNotFound('Not found. Nanana nanère')


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
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('repository', 'repository')
    config.add_route('simple', 'simple/*traverse', factory=root_factory)
    # onfig.add_route('simple', 'simple/*traverse', factory='papaye.root_factory')
    # config.add_view("papaye.views.simple:ListPackagesView", context="BTrees.OOBTree.OOBTree", name="simple", renderer="simple.jinja2", request_method="GET", root_factory=root_factory)
    config.add_notfound_view(notfound, append_slash=True)
    #config.add_request_method(add_db, 'db_env', reify=True)
    #config.add_request_method(get_db_session, 'db', reify=True)
    #start_queue(settings)
    #start_collector(settings)
    #registrer_producer(settings)
    config.scan()
    return config.make_wsgi_app()
