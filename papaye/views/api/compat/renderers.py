from pyramid.interfaces import IRendererFactory


class CompatAPIRendererFactory(object):

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        registry = system['request'].registry
        data = {
            'count': len(value),
            'result': value,
        }
        renderer_factory = registry.getUtility(IRendererFactory, name='json')
        renderer = renderer_factory(self.info)
        return renderer(data, system)

