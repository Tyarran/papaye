import hashlib
import logging
import requests
import transaction

from BTrees.OOBTree import OOBTree
from pyramid_zodbconn import db_from_uri
from termcolor import colored

from papaye.factories import repository_root_factory
from papaye.tasks import task
from papaye.proxy import PyPiProxy


logger = logging.getLogger(__name__)


def get_connection(settings):
    uri = settings.get('zodbconn.uri', None)
    db = db_from_uri(uri, 'unamed', None)
    return db.open()


@task
def download_release_from_pypi(settings, package_name, release_name):
    conn = get_connection(settings)
    proxy = PyPiProxy(conn, package_name)
    package = proxy.build_repository(release_name=release_name)
    if not package:
        logger.error('Package {} not found on PYPI'.format(package_name))
    root = repository_root_factory(conn)
    for release_file in package[release_name].release_files.values():
        print(colored('Download file "{}"'.format(release_file.filename), 'yellow'))
        release_file.set_content(requests.get(release_file.pypi_url).content)
        with release_file.content.open() as content:
            if hashlib.md5(content.read()).hexdigest() != release_file.md5_digest:
                raise IOError('md5 check error')
    root[package.name] = package
    try:
        transaction.commit()
    except:
        transaction.abort()
