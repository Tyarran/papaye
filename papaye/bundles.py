from webassets import Bundle

papaye_css = Bundle(
    'style.css',
    output='gen/css/papaye.css',
    filters='cssmin',
)

external_css = Bundle(
    'includes/bootstrap/css/bootstrap.min.css',
    'includes/font-awesome/css/font-awesome.min.css',
)

papaye_fonts = Bundle(
    'includes/OpenSans/OpenSans-Regular-webfont.woff',
)

papaye_js = Bundle(
    'includes/angular/angular.min.js',
    'includes/angular/angular-route.min.js',
    'includes/angular/angular-resource.min.js',
    'includes/jquery/jquery-2.1.1.min.js',
    'includes/bootstrap/js/bootstrap.min.js',
    'includes/noty/packaged/jquery.noty.packaged.min.js',
    'papaye/app.js',
    'papaye/services.js',
    'papaye/controllers.js',
    output='gen/js/papaye.js',
    filters='jsmin',
)
