import logging

from pyramid.httpexceptions import HTTPInternalServerError


logger = logging.getLogger(__name__)


class BaseView(object):

    def __call__(self):
        super().__call__(self)
        try:
            self.request.db.commit()
        except:
            self.request.db.abort()
            return HTTPInternalServerError()

    def __init__(self, request):
        logger.debug('Dispatch "{}" route as {} with {} method'.format(
            request.matched_route.name,
            request.path,
            request.method
        ))
        self.request = request
        self.settings = request.registry.settings
        self.repository = self.settings.get('papaye.repository')
        proxy = self.settings.get('papaye.proxy', False)
        self.proxy = proxy == 'true' if proxy else False
        self.db = self.request.db
