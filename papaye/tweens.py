from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.response import Response
from pyramid.security import authenticated_userid


class LoginRequiredTweenFactory(object):

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        if isinstance(response, Response) and response.status_int == 401:
            next_value = request.path
            return HTTPTemporaryRedirect(
                request.route_url('login', _query={'next': next_value})
            )
        return response
