import argparse
import getpass
import os
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


def database_already_initialized(dbconn):
    zodb_root = get_database_root(dbconn)
    if not '{}_root'.format(APP_NAME) in zodb_root:
        return False
    if not len([user for user in zodb_root['{}_root'.format(APP_NAME)]['user'] if 'group:admin' in user.groups]):
        return False
    return True


def admin_already_exists(dbconn, username):
    zodb_root = get_database_root(dbconn)
    if not '{}_root'.format(APP_NAME) in zodb_root:
        return False
    users = [user.username for user in zodb_root['{}_root'.format(APP_NAME)]['user'] if user.username == username]
    if users:
        return True
    else:
        return False


def create_app_root(dbconn):
    zodb_root = get_database_root(dbconn)
    if not '{}_root'.format(APP_NAME) in zodb_root:
        zodb_root['{}_root'.format(APP_NAME)] = Root()
    if 'user' not in zodb_root['{}_root'.format(APP_NAME)]:
        zodb_root['{}_root'.format(APP_NAME)]['user'] = Root()
    if 'repository' not in zodb_root['{}_root'.format(APP_NAME)]:
        zodb_root['{}_root'.format(APP_NAME)]['repository'] = Root()


def create_admin_user(dbconn, username, password):
    admin = User(username, password, groups=['group:admin'])
    root = user_root_factory(dbconn)
    root[username] = admin
    transaction.commit()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Initialize the Papaye database.')
    parser.add_argument('file.ini', type=str, nargs='+', help='configuration INI file')
    parser.add_argument('--user', type=str, help='Admin username')
    parser.add_argument('--password', type=str, help='Admin password')
    parser.add_argument('--replace', help='Replace the existing admin user if exists', action='store_true')
    parser.add_argument('-q', help='Quiet mode', dest="quiet", action='store_true')
    return parser.parse_args()


def main(*argv, **kwargs):
    args = parse_arguments()
    if args.quiet:
        sys.stdout = open(os.devnull, "w")
    settings = get_settings(getattr(args, 'file.ini'))
    conn = get_connection(settings)
    if database_already_initialized(conn) and not args.replace:
        print('''There is nothing to do because the database is already initialized.
If you want to force this action, re-run with the "--replace" argument''')
    else:
        if not args.user:
            username = input('username for administrator (default="admin"): ')
            username = 'admin' if not username or username == '' else username.strip()
        else:
            username = args.user
        if not args.password:
            password = getpass.getpass()
        else:
            password = args.password
        if not app_root_exists(conn):
            create_app_root(conn)
        create_admin_user(conn, username, password)
    print("Initialization complete!")
