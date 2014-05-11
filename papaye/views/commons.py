import logging


logger = logging.getLogger(__name__)


class BaseView(object):

    def __init__(self, context, request):
        logger.info('Dispatch "{}" route as {} with {} method'.format(
            request.matched_route.name,
            request.path,
            request.method
        ))
        self.request = request
        self.context = context
        self.settings = request.registry.settings
        proxy = self.settings.get('papaye.proxy', False)
        self.proxy = True if proxy and proxy == 'true' else False
