from webassets import Bundle

noty_js = Bundle(
    'includes/noty/packaged/jquery.noty.packaged.min.js',
)

angular_js = Bundle(
    'includes/angular/angular.min.js',
    'includes/angular/angular-route.min.js',
    'includes/angular/angular-resource.min.js',
)


bootstrap_js = Bundle(
    'includes/jquery/jquery-2.1.1.min.js',
    'includes/bootstrap/js/bootstrap.min.js',
    # angular_js,
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

papaye_js = Bundle(
    angular_js,
    bootstrap_js,
    noty_js,
    'papaye/app.js',
    'papaye/services.js',
    'papaye/controllers.js',
)
