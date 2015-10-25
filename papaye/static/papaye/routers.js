var app = app || {};

(function() {
    'use strict';

    app.appRouter = Backbone.Router.extend({

        routes: {
            "": "home", // url:event that fires
            "/": "home", // url:event that fires
            "home": "home", // url:event that fires
            "browse": "browse", // url:event that fires
        },

        notifyActivePageChange: function(page) {
            app.navView.changeActivePage(page);
        },

        home: function() {
            this.notifyActivePageChange('home');
            var template = _.template($("#index_tmpl").html());
            var content_node = $("#content");

            content_node.html(template({simpleUrl: app.server_vars.simple_route_url}));
        },

        browse: function() {
            this.notifyActivePageChange('browse');
            var content_node = $("#content");

            content_node.html("");
        },
    });
})();
