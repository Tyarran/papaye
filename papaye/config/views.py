from pyramid.httpexceptions import HTTPNotFound
from pyramid.interfaces import ISettings


def notfound(request):
    return HTTPNotFound()


def includeme(config):
    packages_directory = config.registry.getUtility(
        ISettings,
        name='settings',
    )['papaye']['packages_directory']
    config.add_static_view('repo', packages_directory, cache_max_age=3600)
