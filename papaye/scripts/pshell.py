import functools
import transaction

from papaye.factories import user_root_factory, repository_root_factory, default_root_factory


def set_database_version(request, version):
    root = default_root_factory(request)
    root['repoze.evolution'] = {'papaye.evolve': version}
    transaction.commit()


def setup(env):
    env['user_root'] = user_root_factory(env['request'])
    env['repo_root'] = repository_root_factory(env['request'])
    env['default_root'] = default_root_factory(env['request'])
    env['set_db_version'] = functools.partial(set_database_version, env['request'])
