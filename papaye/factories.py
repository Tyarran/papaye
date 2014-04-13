import transaction

from pyramid_zodbconn import get_connection


APP_NAME = __import__(__name__).__name__


def user_root_factory(request):
    from papaye.models import Root
    conn = get_connection(request)
    zodb_root = conn.root()
    if not '{}_root'.format(APP_NAME) in zodb_root:
        zodb_root['{}_root'.format(APP_NAME)] = Root()
        zodb_root['{}_root'.format(APP_NAME)]['user'] = Root()
    return zodb_root['{}_root'.format(APP_NAME)]['user']


def repository_root_factory(request):
    from papaye.models import Root
    conn = get_connection(request)
    zodb_root = conn.root()
    if not '{}_root'.format(APP_NAME) in zodb_root:
        zodb_root['{}_root'.format(APP_NAME)] = Root()
        zodb_root['{}_root'.format(APP_NAME)]['repository'] = Root()
        zodb_root['{}_root'.format(APP_NAME)]['user'] = Root()
        transaction.commit()
    return zodb_root['{}_root'.format(APP_NAME)]['repository']
