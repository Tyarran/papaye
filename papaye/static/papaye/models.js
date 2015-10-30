var app = app || {};

(function(){
    'use strict';

    app.Page = Backbone.Model.extend({
        name: 'Page name',
        //url: 'Page URL'
    });

    app.PackageSummary = Backbone.Model.extend({
        name: "The package name",
        summary: "The package summary",
    });
})();
