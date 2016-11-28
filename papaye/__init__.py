from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings

from papaye.config.utils import SettingsReader


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    config.add_directive('settings_reader', lambda c: SettingsReader(c))
    config.reader = SettingsReader(config)
    config.include('papaye.config.auth')
    config.include('papaye.config.routes')
    config.include('papaye.config.views')
    config.include('papaye.config.startup')
    config.commit()
    config.add_tween('papaye.tweens.LoginRequiredTweenFactory')
    config.scan(ignore='papaye.tests')
    return config.make_wsgi_app()
