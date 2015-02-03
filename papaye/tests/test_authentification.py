from pyramid import testing

from papaye.tests.tools import FakeRoute


def test_instanciate():
    from papaye.authentification import RouteNameAuthPolicy
    from pyramid.authentication import AuthTktAuthenticationPolicy
    auth_policy = AuthTktAuthenticationPolicy('seekreet', hashalg='sha512')

    policy = RouteNameAuthPolicy(home=auth_policy)

    assert policy.policies == {'home': auth_policy}


def test_instanciate_multiple_policies():
    from papaye.authentification import RouteNameAuthPolicy
    from pyramid.authentication import AuthTktAuthenticationPolicy
    auth_policy = AuthTktAuthenticationPolicy('seekreet', hashalg='sha512')
    auth_policy2 = AuthTktAuthenticationPolicy('seekreet_again', hashalg='sha512')

    policy = RouteNameAuthPolicy(home=auth_policy, index=auth_policy2)

    assert policy.policies == {'home': auth_policy, 'index': auth_policy2}


def test_get_policy():
    from papaye.authentification import RouteNameAuthPolicy
    from pyramid.authentication import AuthTktAuthenticationPolicy
    auth_policy = AuthTktAuthenticationPolicy('seekreet', hashalg='sha512')
    policy = RouteNameAuthPolicy(home=auth_policy)
    request = testing.DummyRequest(matched_route=FakeRoute('home'))

    result = policy.get_policy(request)

    assert result
    assert result == auth_policy


def test_get_policy_with_multiple_policies():
    from papaye.authentification import RouteNameAuthPolicy
    from pyramid.authentication import AuthTktAuthenticationPolicy
    auth_policy = AuthTktAuthenticationPolicy('seekreet', hashalg='sha512')
    auth_policy2 = AuthTktAuthenticationPolicy('seekreet2', hashalg='sha512')
    policy = RouteNameAuthPolicy(home=auth_policy)
    request = testing.DummyRequest(matched_route=FakeRoute('home'))

    result = policy.get_policy(request)

    assert result
    assert result is auth_policy
    assert result is not auth_policy2


def test_get_policy_with_default_policy():
    from papaye.authentification import RouteNameAuthPolicy
    from pyramid.authentication import AuthTktAuthenticationPolicy
    auth_policy = AuthTktAuthenticationPolicy('seekreet', hashalg='sha512')
    policy = RouteNameAuthPolicy(default=auth_policy)
    request = testing.DummyRequest(matched_route=FakeRoute('home'))

    result = policy.get_policy(request)

    assert result
    assert result is auth_policy
