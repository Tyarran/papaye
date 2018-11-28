import base64
import json
import logging

import requests
from deform import Form
from deform.exception import ValidationFailure
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED, remember
from pyramid.view import view_config

from papaye.schemas import LoginSchema
from papaye.views.decorators import state_manager

logger = logging.getLogger(__name__)

# @view_config(route_name='home', renderer='index.jinja2', request_method='GET')
# def index_view(context, request):
#     username = request.session.get('username', '')
#     app_context = {
#         'username': username,
#         'papaye': {
#             'debug': False,
#         },
#         'urls':  {
#             'login': request.route_url('login'),
#             'logout': request.route_url('logout'),
#             'package_resource': request.route_url('packages'),
#             'api': request.route_url('api'),
#             'simple': request.route_url('simple', traverse=()),
#         }
#     }
#     return {'app_context': json.dumps(app_context)}
# @view_config(route_name='home', renderer='index.jinja2', request_method='GET')
# @view_config(route_name='home', request_method='GET', renderer='index.jinja2')
def index_view(context, request):
    username = request.session.get("username", "Romain")
    request.state.update(
        {
            "simpleUrl": request.route_url("simple", traverse=()),
            "username": username,
            "navbarBurgerIsActive": False,
            "navMenu": (
                {
                    "id": "home",
                    "title": "Home",
                    "href": "/",
                    "active": True,
                    "exact": True,
                },
                {
                    "id": "browse",
                    "title": "Discover",
                    "href": "/browse",
                    "active": False,
                },
                {"id": "api", "title": "API", "href": "/api", "active": False},
            ),
            "filteredPackageList": requests.get(
                "http://localhost:6543/api/compat/package/json"
            ).json()["result"],
        }
    )
    try:
        result = requests.post(
            "http://localhost:9009/render",
            json={"path": request.path, "state": request.state},
        ).content.decode("utf-8")
    except Exception:
        result = ""
    return {"content": result, "state": json.dumps(request.state)}


@view_config(route_name="ssr", request_method="GET", renderer="index.jinja2")
@state_manager("application")
def index_ssr(request, state):
    try:
        result = requests.post(
            "http://localhost:9009/render",
            json={"path": request.path, "state": state},
        ).content.decode("utf-8")
    except Exception:
        result = ""
    return {"content": result, "state": base64.b64encode(json.dumps(state).encode('utf-8')).decode('utf-8')}


@view_config(
    route_name="login",
    renderer="login.jinja2",
    permission=NO_PERMISSION_REQUIRED,
)
class LoginView(object):
    def __init__(self, request):
        self.request = request
        self.schema = LoginSchema().bind(request=self.request)
        self.form = Form(self.schema, buttons=("submit",))

    def __call__(self):
        return getattr(self, self.request.method.lower())()

    def get(self):
        return {"form": self.form, "request": self.request}

    def post(self):
        controls = self.request.POST.items()
        try:
            validated = self.form.validate(controls)
            headers = remember(self.request, validated["username"])
            self.request.session["username"] = validated["username"]
            csrf_token = self.request.session.get_csrfkj_token()
            headers.append(("X-CSRF-Token", csrf_token))
            next_value = self.request.GET.get("next")
            location = self.request.route_url("home")
            if next_value:
                location = location + next_value[1:]
            return HTTPMovedPermanently(location=location, headers=headers)
        except ValidationFailure:
            return {"form": self.form, "request": self.request}


@view_config(route_name="logout", permission=NO_PERMISSION_REQUIRED)
def logout_view(request):
    from pyramid.security import forget

    if "username" in request.session:
        del request.session["username"]
    headers = forget(request)
    return Response(headers=headers)
