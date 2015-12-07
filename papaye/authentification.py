from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implementer


@implementer(IAuthenticationPolicy)
class RouteNameAuthPolicy(object):

    def __init__(self, **policies):
        self.policies = policies

    def get_policy(self, request):
        if request.matched_route is None:
            return self.policies.get('default')
        else:
            route_name = request.matched_route.name
        return self.policies.get(route_name, self.policies.get('default'))

    def authenticated_userid(self, request):
        return self.get_policy(request).authenticated_userid(request)

    def unauthenticated_userid(self, request):
        return self.get_policy(request).unauthenticated_userid(request)

    def effective_principals(self, request):
        return self.get_policy(request).effective_principals(request)

    def remember(self, request, principal, **kw):
        return self.get_policy(request).remember(request, principal, **kw)

    def forget(self, request):
        return self.get_policy(request).forget(request)
