import hashlib
import logging
import requests
import transaction

from papaye.factories import repository_root_factory
from papaye.tasks import task
from papaye.proxy import PyPiProxy


logger = logging.getLogger(__name__)


def get_connection(config):
    conn = config.registry._zodb_databases[''].open()
    return conn


@task
def download_release_from_pypi(config, package_name, release_name):
    transaction.begin()
    conn = get_connection(config)
    proxy = PyPiProxy(conn, package_name)
    package = proxy.build_repository(release_name=release_name)
    if not package:
        logger.error('Package {} not found on PYPI'.format(package_name))
    root = repository_root_factory(conn)
    for release_file in package[release_name].release_files.values():
        logger.info('Download file "{}"'.format(release_file.filename))
        release_file.set_content(requests.get(release_file.pypi_url).content)
        with release_file.content.open() as content:
            if hashlib.md5(content.read()).hexdigest() != release_file.md5_digest:
                raise IOError('md5 check error')
    root[package.name] = package
    try:
        transaction.commit()
    except:
        transaction.abort()
