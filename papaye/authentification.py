from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implementer

# from pyramid.authentication import (
    # BasicAuthAuthenticationPolicy, AuthTktAuthenticationPolicy
# )
from pyramid.authentication import AuthTktAuthenticationPolicy


@implementer(IAuthenticationPolicy)
class RouteNameAuthPolicy(AuthTktAuthenticationPolicy):

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


@implementer(IAuthenticationPolicy)
class MultipleAuthPolicy(object):

    def __init__(self, *policies):
        self._policies = policies

    @property
    def policies(self):
        return (policy for policy in self._policies)

    def authenticated_userid(self, request):
        policy = next(self.policies)
        return policy.authenticated_userid(request)

    def unauthenticated_userid(self, request):
        policy = next(self.policies)
        return policy.unauthenticated_userid(request)

    def effective_principals(self, request):
        policy = next(self.policies)
        return policy.effective_principals(request)

    def remember(self, request, principal, **kw):
        result = []
        for policy in self.policies:
            result = result + policy.remember(request, principal, **kw)
        return result

    def forget(self, request):
        result = []
        for policy in self.policies:
            result = result + policy.forget(request)
        return result


@implementer(IAuthenticationPolicy)
class RollingAuthPolicy(object):

    def __init__(self, *policies):
        self._policies = policies

    def policies(self):
        return (policy for policy in self._policies)

    def authenticated_userid(self, request):
        default = None
        for policy in self.policies():
            auth_userid = policy.authenticated_userid(request)
            if auth_userid:
                return auth_userid
        return default

    def unauthenticated_userid(self, request):
        default = None
        for policy in self.policies():
            unauth_userid = policy.unauthenticated_userid(request)
            if unauth_userid:
                return unauth_userid
        return default

    def effective_principals(self, request):
        default = []
        for policy in self.policies():
            try:
                return policy.effective_principals(request)
            except:
                pass
        return default

    def remember(self, request, principal, **kw):
        default = None
        for policy in self.policies():
            try:
                return policy.remember(request, principal, **kw)
            except:
                pass
        return default

    def forget(self, request):
        default = None
        for policy in self.policies():
            try:
                return policy.forget(request)
            except:
                pass
        return default
