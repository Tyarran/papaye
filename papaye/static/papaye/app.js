require.config({
   baseUrl: 'static/papaye',
   paths: {
        //bower dependencies
        jquery: '../includes/jquery/dist/jquery',
        backbone: '../includes/backbone/backbone',
        underscore: '../includes/underscore/underscore',
        bootstrap: '../includes/bootstrap/dist/js/bootstrap',
        handlebars: '../includes/handlebars/handlebars',
        text: '../includes/text/text',
        highlightjs: '../includes/highlightjs/highlight.pack',
        noty: '../includes/noty/js/noty/packaged/jquery.noty.packaged',
   },
   shim: {
        'backbone': {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone',
        },
        'underscore': {
            exports: '_'
        },
        'bootstrap': {
            deps: ['jquery', ],
        },
        'handlebars': {
            exports: 'Handlebars',
        },
        'highlightjs': {
            exports: 'hljs',
        },
        'noty': {
            deps: ['jquery', ],
            exports: 'noty',
        },
   }
});


define('common', ['backbone', 'bootstrap', 'text', 'highlightjs', 'helpers', 'noty']);


var dependencies = [
    'common',
    'routers/appRouter',
    'models/Page',
    'views/NavView',
    'models/Registry',
    'views/BreadcrumsView',
    'collections/Breadcrumb',
];


requirejs(dependencies, function(common, appRouter, Page, NavView, registry, BreadcrumsView, Breadcrumb) {

    registry.set('activePage', new Page());
    registry.set('breadcrumbs', new Breadcrumb);

    new BreadcrumsView();

    $.get('api/vars/json', function(data) {
       registry.set('server_vars',  data);
       registry.set('router', new appRouter($("#content")));
       new NavView();
       Backbone.history.start();
    });

    // Override View.remove()'s default behavior
    Backbone.View = Backbone.View.extend({

      remove: function() {
          // Empty the element and remove it from the DOM while preserving events
          $(this.el).empty().detach();

          return this;
      }

    }); 

    window.registry = registry;
});
