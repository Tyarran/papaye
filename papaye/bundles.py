from webassets import Bundle

papaye_css = Bundle(
    'style.css',
    output='gen/css/papaye.css',
    filters='cssmin',
)

font_awesome_css = Bundle(
    'includes/font-awesome/css/font-awesome.css',
)

opensans_css = Bundle(
    'includes/WebFont-OpenSans/css/stylesheet.css',
)

backbone_js = Bundle(
    'includes/underscore/underscore.js',
    'includes/backbone/backbone.js',
)

jquery_js = Bundle(
    'includes/jquery/dist/jquery.js',
)

bootstrap_js = Bundle(
    'includes/bootstrap/dist/js/bootstrap.js',
    'includes/bootstrap/dist/css/bootstrap.css',
)

bootstrap_css = Bundle(
    'includes/bootstrap/dist/css/bootstrap.css',
)

noty_js = Bundle(
    'includes/noty/js/noty/packaged/jquery.noty.packaged.js',
)

highlightjs_js = Bundle(
    'includes/highlightjs/highlight.pack.js',
)

highlightjs_css = Bundle(
    'includes/highlightjs/styles/monokai_sublime.css',
)

handlebars_js = Bundle(
    'includes/handlebars/handlebars.js',
)

requirejs_js = Bundle(
    'includes/requirejs/require.js',
)

bower_js_resources = Bundle(
    jquery_js,
    backbone_js,
    bootstrap_js,
    noty_js,
    highlightjs_js,
    handlebars_js,
)

require_js_resources = Bundle(
    requirejs_js,
)

bower_css_resources = Bundle(
    font_awesome_css,
    bootstrap_css,
    opensans_css,
    highlightjs_css,
)

papaye_js_assets = Bundle(
    bower_js_resources,
    'papaye/helpers.js',
    'papaye/views.js',
    'papaye/models.js',
    'papaye/collections.js',
    'papaye/routers/appRouters.js',
    #'papaye/routers.js',
    'papaye/app.js',
    output='gen/js/papaye.js',
    filters='jsmin',
)
papaye_css_assets = Bundle(
    bower_css_resources,
    papaye_css,
    output='gen/js/papaye.css',
    filters='cssmin',
)
