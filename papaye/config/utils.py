from pyramid.settings import asbool


class SettingsReader(object):

    def __init__(self, config):
        self.config = config
        self.settings = self.config.get_settings()

    def read_bool(self, option, default=False):
        value = self.settings.get(option)
        if not value:
            return default
        else:
            return asbool(value)

    def read_str(self, option, default=None):
        return self.settings.get(option, default)
