from papaye.factories import user_root_factory, repository_root_factory


def setup(env):
    env['user_root'] = user_root_factory(env['request'])
    env['repository_root'] = repository_root_factory(env['request'])
