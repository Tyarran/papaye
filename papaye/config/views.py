from pyramid.httpexceptions import HTTPNotFound


def notfound(request):
    return HTTPNotFound()


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    # config.add_notfound_view(notfound, append_slash=True)
