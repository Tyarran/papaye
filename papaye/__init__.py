from os import makedirs
from os.path import exists
from pyramid.config import Configurator, ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from CodernityDB.database import Database
from pyramid.security import Allow, Everyone

from papaye.indexes import INDEXES

authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
authz_policy = ACLAuthorizationPolicy()


def get_db(request):
    database_path = request.registry.settings['codernity.url'][7:]
    db = Database(database_path)
    if not db.exists():
        db.create()
        for name, index_class in INDEXES:
            index = index_class(db.path, name)
            db.add_index(index)
    else:
        db.open()
    return db


class RootFactory(object):
    """
    Pyramid root factory that contains the ACL.
    """
    __name__ = None
    __parent__ = None
    root = None

    class Root(object):
        __acl__ = None

    def __init__(self, settings):
        self.root = self.root if self.root is not None else self.Root()
        if self.root.__acl__ is None:
            self.root.__acl__ = self.read_acl_from_settings()

    def __call__(self, request):
        return self.root

    def read_acl_from_settings(self):
        #credentials = [
        #    (Allow, 'group:Admin', ALL_PERMISSIONS),
        #    (Allow, 'group:Publisher', 'publish'),
        #    (Allow, 'group:Installer', 'install'),
        #    (Allow, Authenticated, 'install'),
        #]
        credentials = [
            (Allow, Everyone, 'install'),
            (Allow, Everyone, 'publish'),
        ]
        return credentials


def notfound(request):
    return HTTPNotFound('Not found, bro.')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    repository = settings.get('papaye.repository', None)
    if not repository:
        raise ConfigurationError('Variable {} missing in settings'.format('papaye.repository'))
    elif not exists(repository):
        makedirs(repository)
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings, root_factory=RootFactory(settings))
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
    config.add_request_method(get_db, 'db', reify=True)
    config.scan()
    return config.make_wsgi_app()
