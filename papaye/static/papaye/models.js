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
        
        initialize: function(options) {
            this.name = options.packageName;
            this.version = options.version;
        },

        url: function() {
            var url = '/api/package/' + this.name + '/json';

            console.log(this.version);
            if (this.version !== undefined && this.version !== null) {
                url = '/api/package/' + this.name + '/' + this.version + '/json'
            }
            return url;
        },
    });
})();
