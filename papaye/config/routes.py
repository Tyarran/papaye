from papaye.factories.root import (
    user_root_factory,
    application_factory,
)


def includeme(config):
    config.add_route('login', '/login/', factory=user_root_factory)
    config.add_route('logout', '/logout/')
    config.add_route('home', '/', factory=application_factory)
    config.add_route('api', '/api/', factory=user_root_factory)
    config.add_route(
        'simple',
        '/simple*traverse',
        factory='papaye.factories.root:repository_root_factory',
    )
