from pyramid.httpexceptions import HTTPNotFound


def notfound(request):
    return HTTPNotFound()


def includeme(config):
    config.add_static_view('static', 'papaye:static', cache_max_age=3600)
