import logging
import requests

from beaker.cache import cache_region


logger = logging.getLogger(__name__)


class ExistsOnPyPIMixin(object):

    @cache_region('pypi', 'get_last_remote_filename')
    def exists_on_pypi(self, pypi_url):
        try:
            result = requests.get(pypi_url)
            if result.status_code == 200:
                return result
            else:
                return None
        except:
            logger.warning('Bad url "{}"'.format(pypi_url))
            return None
