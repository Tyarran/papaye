import hashlib
import logging
import requests
import transaction

from papaye.factories import repository_root_factory
from papaye.models import Package
from papaye.proxy import PyPiProxy
from papaye.tasks import task


logger = logging.getLogger(__name__)


def get_connection(config):
    conn = config.registry._zodb_databases[''].open()
    return conn


@task
def download_release_from_pypi(config, package_name, release_name):
    # if not package:
    #     logger.error('Package {} not found on PYPI'.format(package_name))
    repository_is_updated = False
    conn = get_connection(config)
    proxy = PyPiProxy()
    root = repository_root_factory(conn)
    local_package = root[package_name]
    if local_package is None:
        local_package = Package(package_name)
        created_package = True
    else:
        created_package = False
    # package = proxy.build_remote_repository(package.__name__, metadata=True)
    merged_repository = proxy.merged_repository(
        local_package,
        metadata=True,
        release_name=release_name,
        root=root
    )

    for release_file in merged_repository[package_name][release_name].release_files.values():
        if release_file.__name__ not in list(local_package.releases):
            logger.info('Download file "{}"'.format(release_file.filename))
            release_file.set_content(requests.get(release_file.pypi_url).content)
            with release_file.content.open() as content:
                binary_content = content.read()
                if hashlib.md5(binary_content).hexdigest() != release_file.md5_digest:
                    continue
            release_file.size = len(binary_content)
            repository_is_updated = True
    if repository_is_updated:
        transaction.commit()
    else:
        if created_package:
            del(root[package_name])
        transaction.abort()
