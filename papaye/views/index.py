from pyramid.response import Response
from pyramid.security import remember
from pyramid.view import forbidden_view_config
from pyramid.view import view_config


@view_config(route_name='home', renderer='index.jinja2')
def index_view(context, request):
    return {"username": request.session.get('username', '')}


@forbidden_view_config(route_name='home', renderer='json')
def forbidden_browse_view(request):
    return Response(status_code=401)


@view_config(route_name='islogged', renderer='json', permission="test")
def index_view2(request):
    username = request.session.get('username', None)
    if not username:
        return Response(status_code=401)
    return username


@forbidden_view_config(route_name='islogged', renderer='json')
def forbidden_view(request):
    return Response(status_code=401)


@view_config(route_name="login", renderer="json")
def login_view(request):
    login = request.POST.get('login')
    password = request.POST.get('password')
    if login in request.root and request.root[login].password_verify(password):
        headers = remember(request, 'test')
        request.session['username'] = login
        return Response(login, headers=headers)
    else:
        return Response(status_code=401)


@view_config(route_name="logout")
def logout_view(request):
    from pyramid.security import forget
    if 'username' in request.session:
        del request.session['username']
    headers = forget(request)
    return Response(headers=headers)
