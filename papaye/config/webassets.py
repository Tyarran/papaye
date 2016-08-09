from papaye.bundles import (
    papaye_css_assets,
    papaye_js_assets,
    require_js_resources,
)


WEBASSETS_DEFAULT_CONFIG = {
    "debug": False,
    "updater": 'timestamp',
    "cache": True,
    "url_expire": False,
    "static_view": True,
    "cache_max_age": 3600,
}


def includeme(config):
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    config.include('pyramid_webassets')
    assets_env = config.get_webassets_env()
    for item in WEBASSETS_DEFAULT_CONFIG.items():
        assets_env.config.setdefault(*item)
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.assets_environment = assets_env
    config.add_webasset('papaye_js_assets', papaye_js_assets)
    config.add_webasset('papaye_css_assets', papaye_css_assets)
    config.add_webasset('requirejs', require_js_resources)
