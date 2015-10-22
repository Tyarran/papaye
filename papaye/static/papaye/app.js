var app = app || {};

(function($, B) {
   'use strict';

    $('document').ready(function() {
        new app.appView();
        app.navView = new app.NavView();
        app.content = new app.contentView();
        app.router = new app.appRouter();
        B.history.start();
    });
})(jQuery, Backbone);
