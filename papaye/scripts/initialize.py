import getpass
import sys
import transaction

from papaye.scripts.common import get_settings
from papaye.factories import user_root_factory, APP_NAME
from papaye.models import User, Root, get_connection


def get_database_root(dbconn):
    zodb_root = dbconn.root()
    return zodb_root


def app_root_exists(dbconn):
    zodb_root = get_database_root(dbconn)
    if not '{}_root'.format(APP_NAME) in zodb_root:
        return False
    return True


def create_app_root(dbconn):
    zodb_root = get_database_root(dbconn)
    if not '{}_root'.format(APP_NAME) in zodb_root:
        zodb_root['{}_root'.format(APP_NAME)] = Root()
    if not 'user' in zodb_root['{}_root'.format(APP_NAME)]:
        zodb_root['{}_root'.format(APP_NAME)]['user'] = Root()
    if not 'repository' in zodb_root['{}_root'.format(APP_NAME)]:
        zodb_root['{}_root'.format(APP_NAME)]['repository'] = Root()


def create_admin_user(dbconn):
    username = input('username for administrator (default="admin"): ')
    username = 'admin' if not username or username == '' else username
    password = getpass.getpass()
    admin = User(username, password, groups=['group:admin'])
    root = user_root_factory(dbconn)
    root[username] = admin
    transaction.commit()


def main(*argv, **kwargs):
    settings = get_settings(sys.argv[1])
    conn = get_connection(settings)
    if not app_root_exists(conn):
        create_app_root(conn)
    create_admin_user(conn)
    print("Initialization complete!")
