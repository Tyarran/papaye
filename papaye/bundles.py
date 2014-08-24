from webassets import Bundle

jst = Bundle(
    'templates/*.html',
    filters='jst',
    output='test.js',
    debug=False
)

bootstrap_js = Bundle(
    'includes/jquery/jquery-2.1.1.min.js',
    'includes/bootstrap/js/bootstrap.min.js',
    output='gen/packed.js'
)

bootstrap_css = Bundle('includes/bootstrap/css/bootstrap.min.css')
papaye_css = Bundle(
    bootstrap_css,
    'style.css',
    output='gen/papaye.css',
)
papaye_font = Bundle(
    'includes/OpenSans/OpenSans-Regular-webfont.woff',
)
