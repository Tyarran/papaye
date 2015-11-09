var app = app || {};

(function(){
    'use strict';

    app.Page = Backbone.Model.extend({
        name: 'Page name',
        url: 'Page URL',
    });

    app.PackageSummary = Backbone.Model.extend({
        name: "The package name",
        summary: "The package summary",
    });

    app.Release = Backbone.Model.extend({
        //name: 'object name'
        
        initialize: function(packageName) {
            this.name = packageName;
        },

        url: function() {
            return '/api/package/' + this.name + '/json';
        },
    });
})();
