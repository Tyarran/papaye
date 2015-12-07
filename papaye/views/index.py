import json
import logging

from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response
from pyramid.security import remember
from pyramid.view import forbidden_view_config
from pyramid.view import view_config


from papaye.models import User


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


#@forbidden_view_config(route_name='home', renderer='json')
#def forbidden_browse_view(request):
#    keturn Response(status_code=401)


@view_config(route_name='islogged', renderer='json', permission="test")
def is_logged(request):
    print(request.session)
    username = request.session.get('username', None)
    if not username:
        return Response(status_code=401)
    return username


#@forbidden_view_config(route_name='islogged', renderer='json')
#def forbidden_view(request):
    #return HTTPForbidden()
    #return Response(status_code=401)


@view_config(route_name="login")
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username in [user.username for user in list(request.root)] and request.root[username].password_verify(password):
        headers = remember(request, 'test')
        request.session['username'] = username
        headers.append(('Content-Type', 'application/json; charset=UTF-8'))
        import pprint
        pprint.pprint(headers)
        return Response(json.dumps(username), headers=headers)
    else:
        return Response(json.dumps(None), status_code=401, content_type='application/json', charset='utf-8')


@view_config(route_name="logout")
def logout_view(request):
    from pyramid.security import forget
    if 'username' in request.session:
        del request.session['username']
    headers = forget(request)
    return Response(headers=headers)
