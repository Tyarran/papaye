import argparse
import getpass
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
    if 'user' not in zodb_root['{}_root'.format(APP_NAME)]:
        zodb_root['{}_root'.format(APP_NAME)]['user'] = Root()
    if 'repository' not in zodb_root['{}_root'.format(APP_NAME)]:
        zodb_root['{}_root'.format(APP_NAME)]['repository'] = Root()


def create_admin_user(dbconn, username, password):
    if not username:
        username = input('username for administrator (default="admin"): ')
        username = 'admin' if not username or username == '' else username
    if not password:
        password = getpass.getpass()
    admin = User(username, password, groups=['group:admin'])
    root = user_root_factory(dbconn)
    root[username] = admin
    transaction.commit()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Initialize Papaye database.')
    parser.add_argument('file.ini', type=str, nargs='+', help='configuration INI file')
    parser.add_argument('--user', type=str, help='Admin username')
    parser.add_argument('--password', type=str, help='Admin password')
    return parser.parse_args()


def main(*argv, **kwargs):
    args = parse_arguments()
    settings = get_settings(getattr(args, 'file.ini'))
    conn = get_connection(settings)
    if not app_root_exists(conn):
        create_app_root(conn)
    create_admin_user(conn, args.user, args.password)
    print("Initialization complete!")
