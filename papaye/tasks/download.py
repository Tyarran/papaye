import hashlib
import logging
import requests
import transaction

from pyramid.threadlocal import get_current_request

from papaye.factories import repository_root_factory
from papaye.tasks import task
from papaye.proxy import PyPiProxy


logger = logging.getLogger(__name__)


@task
def download_release_from_pypi(package_name, release_name):
    request = get_current_request()
    proxy = PyPiProxy(request, package_name)
    package = proxy.build_repository()
    if not package:
        logger.error('Package {} not found on PYPI'.format(package_name))
    root = repository_root_factory(request)
    for release_file in package[release_name].release_files.values():
        release_file.content = requests.get(release_file.pypi_url).content.read()
        if hashlib.md5(release_file.content).hexdigest() != release_file.md5_digest:
            raise IOError('md5 check error')
    root[package.name] = package
    try:
        transaction.commit()
    except:
        transaction.abort()
