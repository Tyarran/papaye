from pyramid.view import view_config

from papaye.views.commons import BaseView


@view_config(route_name="home", renderer='home.jinja2')
class HomeView(BaseView):

    def __call__(self):
        return {'message': 'ok'}
