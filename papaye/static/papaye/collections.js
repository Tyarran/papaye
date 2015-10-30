var app = app || {};

(function(){
    'use strict';

    app.PageCollection = Backbone.Collection.extend({
        model: app.Page,
    });

    app.PackageSummaryCollection = Backbone.Collection.extend({
        url: "/api/package/json",
        model: app.PackageSummary,

        parse: function(response, options) {
            return response.result;
        }
    });
})();
