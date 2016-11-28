from pyramid.config import Configurator
from pyramid.settings import asbool


class SettingsReader(object):

    def __init__(self, configuration_or_settings):
        self.settings = self.get_settings(configuration_or_settings)

    def get_settings(self, configuration_or_settings):
        if isinstance(configuration_or_settings, Configurator):
            return configuration_or_settings.get_settings()
        else:
            return configuration_or_settings

    def read_bool(self, option, default=False):
        value = self.settings.get(option)
        if not value:
            return default
        else:
            return asbool(value)

    def read_str(self, option, default=None):
        return self.settings.get(option, default)
