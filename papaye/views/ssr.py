import requests

from papaye.views.decorators import state_manager
from papaye.utils import filter_set


def app_state_factory(request):
    username = request.session.get("username", "Romain")
    state = {
        "simpleUrl": request.route_url("simple", traverse=()),
        "compatAPIUrl": request.route_url("compat_api"),
        "username": username,
        "navbarBurgerIsActive": False,
        "filteredPackageList": [],
        "navMenu": (
            {"id": "home", "title": "Home", "href": "/", "exact": True},
            {"id": "browse", "title": "Discover", "href": "/browse"},
            {"id": "api", "title": "API", "href": "/api"},
        ),
        "detail": {"package": None},
    }
    return state


router = state_manager.router
router.add_route('home', '/', exact=True)
router.add_route('browse', '/browse', exact=True)
router.add_route('detail', '/browse/detail/:appname')


route = state_manager.route_factory("application", app_state_factory)


@route("/")
def home(request, state):
    state["navMenu"] = list(
        filter_set(lambda x: x["href"] == "/" or x["href"] == "", state["navMenu"], "active", True)
    )
    return state


@route("/browse")
def test_view(request, state):
    state["navMenu"] = list(
        filter_set(
            lambda x: x["href"] == "/browse", state["navMenu"], "active", True
        )
    )
    compat_api_packages_url = request.route_url("compat_api_packages")
    state["filteredPackageList"] = requests.get(compat_api_packages_url).json()[
        "result"
    ]
    return state


@route("/browse/detail/:appname")
def package_detail(request, state):
    state["navMenu"] = list(
        filter_set(
            lambda x: x["href"] == "/browse", state["navMenu"], "active", True
        )
    )
    compat_api_package_url = request.route_url(
        "compat_api_package",
        package_name=request.ssr.matchdict["appname"],
    )
    state["detail"] = {
        "package": requests.get(compat_api_package_url).json()["result"]
    }
    return state
