from pyramid.httpexceptions import HTTPNotFound
from pyramid.interfaces import ISettings

from papaye.config.utils import SettingsReader


def notfound(request):
    return HTTPNotFound()


def includeme(config):
    settings = config.registry.getUtility(ISettings)
    packages_directory = SettingsReader(settings).read_str(
        'papaye.packages_directory'
    )
    config.add_static_view('static', 'papaye:static', cache_max_age=3600)
    config.add_static_view('repo', packages_directory, cache_max_age=3600)
