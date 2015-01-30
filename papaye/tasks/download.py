import hashlib
import json
import logging
import requests
import transaction

from papaye.factories import repository_root_factory
from papaye.models import Package
from papaye.proxy import PyPiProxy, smart_merge
from papaye.tasks import task
from papaye.schemas import Metadata


logger = logging.getLogger(__name__)


def get_connection(config):
    conn = config.registry._zodb_databases[''].open()
    return conn


def get_release_metadatas(package_name, release_name):
    schema = Metadata()
    response = requests.get('https://pypi.python.org/pypi/{}/{}/json'.format(package_name, release_name))
    if response.status_code == 200:
        original_metadata = json.loads(response.content.decode('utf-8'))['info']
    return original_metadata, schema.deserialize(schema.serialize(original_metadata))


@task
def download_release_from_pypi(config, package_name, release_name):
    repository_is_updated = False
    conn = get_connection(config)
    proxy = PyPiProxy()
    root = repository_root_factory(conn)
    local_package = root[package_name]
    if local_package is None:
        local_package = Package(package_name)

    remote_repository = proxy.build_remote_repository(
        package_name,
        metadata=True,
        release_name=release_name,
    )

    original_metadata, metadata = get_release_metadatas(package_name, release_name)
    remote_repository[package_name][release_name].original_metadata = original_metadata
    remote_repository[package_name][release_name].metadata = metadata

    for release_file in remote_repository[package_name][release_name].release_files.values():

        if release_file.__name__ not in list(local_package.releases):
            logger.info('Download file "{}"'.format(release_file.filename))
            response = requests.get(release_file.pypi_url)
            if response.status_code == 200:
                release_file.set_content(response.content)
                if release_file.md5_digest != hashlib.md5(response.content).hexdigest():
                    continue
                repository_is_updated = True
            release_file.size = len(release_file.content.open().read())
    if repository_is_updated:
        smart_merge(local_package, remote_repository[package_name], root=root)
        transaction.commit()
    else:
        transaction.abort()
    conn.close()
