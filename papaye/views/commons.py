import logging


logger = logging.getLogger(__name__)


class BaseView(object):

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.settings = request.registry.settings
        proxy = self.settings.get('papaye.proxy', False)
        self.proxy = True if proxy and proxy == 'true' else False
