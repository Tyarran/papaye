var app = app || {};

(function($, B) {
   'use strict';

    $('document').ready(function() {
        $.get('api/vars/json', function(data) {
            app.server_vars = data;
            new app.appView();
            app.navView = new app.NavView();
            app.router = new app.appRouter($("#content"));
            B.history.start();
        });
    });

    // Override View.remove()'s default behavior
    Backbone.View = Backbone.View.extend({

        remove: function() {
            // Empty the element and remove it from the DOM while preserving events
            $(this.el).empty().detach();

            return this;
        }

    }); 
})(jQuery, Backbone);
