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
    try:
        repository_is_updated = False
        conn = get_connection(config)
        proxy = PyPiProxy(conn, package_name)
        root = repository_root_factory(conn)
        package = proxy.build_repository(release_name=release_name, with_metadata=True)
        if not package:
            logger.error('Package {} not found on PYPI'.format(package_name))
        for release_file in package[release_name].release_files.values():
            logger.info('Download file "{}"'.format(release_file.filename))
            release_file.set_content(requests.get(release_file.pypi_url).content)
            with release_file.content.open() as content:
                binary_content = content.read()
                if hashlib.md5(binary_content).hexdigest() != release_file.md5_digest:
                    continue
                    # raise IOError('md5 check error')
            release_file.size = len(binary_content)
            repository_is_updated = True
            
        if repository_is_updated:
            root[package.name] = package
            for release in package:
                release.__parent__ = package
                for release_file in release:
                    release_file.__parent__ = release

        transaction.commit()
    except:
        transaction.abort()
