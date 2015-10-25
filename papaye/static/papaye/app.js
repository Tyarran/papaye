var app = app || {};

(function($, B) {
   'use strict';

    $('document').ready(function() {
        $.get('api/vars/json', function(data) {
                console.log(data);
                app.server_vars = data;
                new app.appView();
                app.navView = new app.NavView();
                app.content = new app.contentView();
                app.router = new app.appRouter();
                B.history.start();

                hljs.initHighlighting();
        });
        //hljs.initHighlighting();
    });
})(jQuery, Backbone);
