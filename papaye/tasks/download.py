import hashlib
import json
import logging
import requests
import transaction

from pyramid.threadlocal import get_current_request

from papaye.factories import repository_root_factory
from papaye.models import ReleaseFile, Package, Release
from papaye.tasks import task


logger = logging.getLogger(__name__)


@task
def download_release_from_pypi(url, release_name):
    try:
        request = get_current_request()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                package_info = json.loads(response.content)
            else:
                logger.error("Received {} status code {} on {}".format(response.status_code,
                                                                       url))
        except ConnectionError:
            logger.error("Connection error")

        package_name = package_info['info']['name']
        root = repository_root_factory(request)
        package = Package.by_name(package_name, request)
        package = package if package else Package(package_name)
        root[package.name] = package
        release = package[release_name] if Release.by_packagename(package_name, request) else Release(release_name,
                                                                                                      release_name)
        root[package.__name__][release.__name__] = release

        release_files_doc = package_info['releases'][release_name]
        for release_doc in release_files_doc:
            infos = {
                'md5_digest': release_doc['md5_digest'],
                'filename': release_doc['filename'],
                'content': requests.get(release_doc['url']).content.read(),
            }
            if not hashlib.md5(infos['content']).hexdigest() == infos['md5_digest']:
                raise IOError('md5 check error')
            release_file = ReleaseFile(**infos)
            root[package.__name__][release.__name__][release_file.__name__] = release_file
        transaction.commit()
    except:
        transaction.abort()
