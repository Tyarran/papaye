import requests

from papaye.views.decorators import state_manager
from papaye.utils import filter_set


def app_state_factory(context, request):
    username = request.session.get("username", "Romain")
    # path = f"/{'/'.join(request.matchdict['path'])}"
    state = {
        "simpleUrl": request.route_url("simple", traverse=()),
        "username": username,
        "navbarBurgerIsActive": False,
        "filteredPackageList": [],
        "navMenu": (
            {"id": "home", "title": "Home", "href": "/", "exact": True},
            {"id": "browse", "title": "Discover", "href": "/browse"},
            {"id": "api", "title": "API", "href": "/api"},
        ),
    }
    return state


route = state_manager.router("application", app_state_factory)


@route("/")
def home(context, request, state):
    state["navMenu"] = list(
        filter_set(lambda x: x["href"] == "/", state["navMenu"], "active", True)
    )
    return state


@route("/browse")
def test_view(context, request, state):
    state["navMenu"] = list(
        filter_set(
            lambda x: x["href"] == "/browse", state["navMenu"], "active", True
        )
    )
    state["filteredPackageList"] = requests.get(
        "http://localhost:6543/api/compat/package/json"
    ).json()["result"]
    return state


@route("/browse/detail/:appname")
def package_detail(context, request, state):
    state["navMenu"] = list(
        filter_set(
            lambda x: x["href"] == "/browse", state["navMenu"], "active", True
        )
    )
    return state
