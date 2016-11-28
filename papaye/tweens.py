from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.response import Response


class LoginRequiredTweenFactory(object):

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def _redirect_to_login(self, request):
        next_value = request.path
        return HTTPTemporaryRedirect(
            request.route_url('login', _query={'next': next_value})
        )

    def __call__(self, request):
        response = self.handler(request)
        if isinstance(response, Response) and response.status_int == 401 and request.matched_route.name == 'default':
            return self._redirect_to_login(request)
        if response.status_int == 403 and request.authenticated_userid is None:
            return self._redirect_to_login(request)
        return response
