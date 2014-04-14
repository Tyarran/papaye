import getpass
import sys
import transaction

from pyramid import testing

from papaye.scripts.common import get_settings
from papaye.factories import user_root_factory
from papaye.models import User


def create_admin_user(settings):
    username = input('username for administrator (default="admin"): ')
    username = 'admin' if not username or username == '' else username
    password = getpass.getpass()
    admin = User(username, password)
    request = testing.DummyRequest()
    config = testing.setUp(request=request, settings=settings)
    config.include('pyramid_zodbconn')
    root = user_root_factory(request)
    root[username] = admin
    transaction.commit()


def main(*argv, **kwargs):
    settings = get_settings(sys.argv[1])
    create_admin_user(settings)
    print("Initialization complete!")
