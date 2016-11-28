import json
import logging

from deform import Form
from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.response import Response
from pyramid.security import remember, NO_PERMISSION_REQUIRED
from pyramid.view import view_config

from papaye.schemas import LoginSchema


logger = logging.getLogger(__name__)


@view_config(route_name='home', renderer='index.jinja2', request_method='GET')
def index_view(context, request):
    username = request.session.get('username', '')
    app_context = {
        'username': username,
        'papaye': {
            'debug': False,
        },
        'urls':  {
            'login': request.route_url('login'),
            'logout': request.route_url('logout'),
            'package_resource': request.route_url('packages'),
            'api': request.route_url('api'),
            'simple': request.route_url('simple', traverse=()),
        }
    }
    return {'app_context': json.dumps(app_context)}


@view_config(route_name="login", renderer='login.jinja2',
             permission=NO_PERMISSION_REQUIRED)
class LoginView(object):

    def __init__(self, request):
        self.request = request
        self.schema = LoginSchema().bind(request=self.request)

    def __call__(self):
        return getattr(self, self.request.method.lower())()

    def get(self):
        form = Form(self.schema, buttons=('submit', ))
        return {'form': form, 'request': self.request}

    def post(self):
        data = self.schema.deserialize(self.request.POST)
        username_matching_users = [user for user in self.request.root
                                   if user.username == data['username']]
        if len(username_matching_users):
            user = username_matching_users[0]
            if user.password_verify(data['password']):
                headers = remember(self.request, user.username)
                self.request.session['username'] = user.username
                csrf_token = self.request.session.get_csrf_token()
                headers.append(('X-CSRF-Token', csrf_token))
                next_value = self.request.GET.get('next')
                if next_value:
                    location = self.request.route_url('home') + next_value[1:]
                else:
                    location = self.request.route_url('home')
                return HTTPTemporaryRedirect(location=location, headers=headers)
        return Response(
            json.dumps(None),
            status_code=401,
            content_type='application/json',
            charset='utf-8'
        )


@view_config(route_name="logout", permission=NO_PERMISSION_REQUIRED)
def logout_view(request):
    from pyramid.security import forget
    if 'username' in request.session:
        del request.session['username']
    headers = forget(request)
    return Response(headers=headers)
