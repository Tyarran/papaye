from os import makedirs
from os.path import exists
from pyramid.config import Configurator, ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
)


def notfound(request):
    return HTTPNotFound('Not found, bro.')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    repository = settings.get('papaye.repository', None)
    if not repository:
        raise ConfigurationError('Variable {} missing in settings'.format('papaye.repository'))
    elif not exists(repository):
        makedirs(repository)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('repository', 'repository')
    config.add_route('simple', '/simple/')
    config.add_route('simple_release', '/simple/{package}/')
    config.add_route('download_release', '/simple/{package}/{release}')
    config.add_notfound_view(notfound, append_slash=True)
    config.scan()
    return config.make_wsgi_app()
