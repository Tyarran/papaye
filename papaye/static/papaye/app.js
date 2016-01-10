var app = app || {};

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
   }
});


define('common', ['backbone', 'bootstrap', 'text', 'highlightjs', 'helpers']);


requirejs(['common', 'routers/appRouter', 'models/Page', 'views/NavView'], function(common, appRouter, Page, NavView) {

    $.get('api/vars/json', function(data) {
        app.server_vars = data;
        app.router = new appRouter($("#content"));
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

    app.activePage = new Page();
});
