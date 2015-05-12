import json
import logging
import requests
import time
import transaction

from ZODB.DB import DB

from papaye.factories import repository_root_factory
from papaye.models import Package, Release, ReleaseFile
from papaye.proxy import download_file
from papaye.tasks import task


logger = logging.getLogger(__name__)


def get_release_metadata(package_name, release_name):
    response = requests.get('https://pypi.python.org/pypi/{}/{}/json'.format(package_name, release_name))
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


@task
def test_func(*args, **kwargs):
    for index in range(0, 10):
        print(index)
        time.sleep(1)


@task
def download_release_from_pypi(db_or_root, package_name, release_name, filename):
    db = isinstance(db_or_root, DB)
    if db:
        conn = db_or_root.open()
        root = repository_root_factory(conn)
    else:
        root = db_or_root
    metadata = get_release_metadata(package_name, release_name)

    for attempt in transaction.attempts():
        with attempt:
            if root[package_name] is None:
                root[package_name] = Package(package_name)
            release_ready_exists = release_name in root[package_name]
            if not release_ready_exists:
                root[package_name][release_name] = Release(
                    release_name,
                    release_name,
                    metadata['info'],
                    deserialize_metadata=True
                )

            if filename not in root[package_name][release_name]:
                release = [release for release in metadata['releases'][release_name]
                           if release['filename'] == filename][0]
                url = release['url']
                md5_digest = release['md5_digest']
                content = download_file(filename, url, md5_digest)
                if not content:
                    transaction.abort()
                    return None
                root[package_name][release_name][filename] = ReleaseFile(filename, content, md5_digest)
    if db:
        conn.close()
