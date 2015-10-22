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

        home: function() {
            console.log("home");
            var template = _.template($("#index_tmpl").html());
            var content_node = $("#content");

            content_node.html(template({simpleUrl: 'http://localhost:6543/simple'}));
        },

        browse: function() {
            console.log("browse");
            var content_node = $("#content");

            content_node.html("");
        },

        toto: function() {
            alert('toto!!!!');
            console.log("toto");
        }

    });
})();
