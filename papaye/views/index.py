import json
import logging

from deform import Form
from pyramid.httpexceptions import HTTPForbidden, HTTPTemporaryRedirect
from pyramid.response import Response
from pyramid.security import remember, NO_PERMISSION_REQUIRED
from pyramid.view import forbidden_view_config
from pyramid.view import view_config

from papaye.models import User
from papaye.schemas import LoginSchema


logger = logging.getLogger(__name__)


@view_config(route_name='home', renderer='index.jinja2')
def index_view(context, request):
    username = request.session.get('username', '')
    result = {'username': username}
    if username == '':
        result['admin'] = False
    else:
        result['admin'] = True if 'group:admin' in User.by_username(username, request).groups else False
    return result


@view_config(route_name="login", renderer='login.jinja2', permission=NO_PERMISSION_REQUIRED)
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
                headers = remember(self.request, 'user')
                self.request.session['username'] = user.username
                csrf_token = self.request.session.get_csrf_token()
                headers.append(('X-CSRF-Token', csrf_token))
                headers.append(
                    ('Content-Type', 'application/json; charset=UTF-8')
                )
                next_value = self.request.GET.get('next')
                if next_value:
                    location = self.request.route_url('home') + next_value[1:]
                else:
                    location = self.request.route_url('home')
                return HTTPTemporaryRedirect(location=location,
                                             headers=headers)
        return Response(
            json.dumps(None),
            status_code=401,
            content_type='application/json',
            charset='utf-8'
        )



# @view_config(route_name="login", request_method='POST', permission=NO_PERMISSION_REQUIRED)
# def login_view(request):
#     import pdb; pdb.set_trace()
#     username = request.POST.get('email')
#     password = request.POST.get('password')
#     if username in [user.username for user in list(request.root)] and request.root[username].password_verify(password):
#         headers = remember(request, 'group:admin')
#         request.session['username'] = username
#         csrf_token = request.session.get_csrf_token()
#         headers.append(('X-CSRF-Token', csrf_token))
#         headers.append(('Content-Type', 'application/json; charset=UTF-8'))
#         return Response(json.dumps(username), headers=headers)
#     else:
#         return Response(json.dumps(None), status_code=401, content_type='application/json', charset='utf-8')


# @view_config(route_name="login", renderer='login.jinja2', permission=NO_PERMISSION_REQUIRED)
# @view_config(route_name="login", request_method='GET', renderer='login.jinja2', permission=NO_PERMISSION_REQUIRED)
# def login_view(request):
#     import pdb; pdb.set_trace()
#     schema = LoginSchema().bind(request=request)
#     form = Form(schema, buttons=('submit', ))
#     # return {'form': form}
#     return {'form': form, 'request': request}



@view_config(route_name="logout")
def logout_view(request):
    from pyramid.security import forget
    if 'username' in request.session:
        del request.session['username']
    headers = forget(request)
    return Response(headers=headers)
