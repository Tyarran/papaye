from pyramid.view import view_config


@view_config(route_name='browse', renderer='index.jinja2')
def index_view(request):
    return {}
