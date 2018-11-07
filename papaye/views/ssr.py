import requests

from papaye.views.decorators import state_manager


def app_state_factory(context, request):
    username = request.session.get('username', 'Romain')
    path = f"/{'/'.join(request.matchdict['path'])}"
    state = {
        'simpleUrl': request.route_url('simple', traverse=()),
        'username': username,
        'navbarBurgerIsActive': False,
        'filteredPackageList': [],
    }
    nav_menu = (
        {
            'id': 'home',
            'title': 'Home',
            'href': '/',
            'exact': True,
        },
        {
            'id': 'browse',
            'title': 'Discover',
            'href': '/browse',
        },
        {
            'id': 'api',
            'title': 'API',
            'href': '/api',
        }
    )

    def set_active(item):
        item['active'] = item['href'] == path
        return item

    state['navMenu'] = list(map(set_active, nav_menu))
    return state


route = state_manager.router('application', app_state_factory)


@route('/browse')
def test_view(context, request, state):
    state['filteredPackageList'] = requests.get(
        'http://localhost:6543/api/compat/package/json'
    ).json()['result']
    return state
