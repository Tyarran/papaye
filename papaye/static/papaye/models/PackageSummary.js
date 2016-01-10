define('models/PackageSummary', ['common', ], function() {

    return Backbone.Model.extend({
        name: "The package name",
        summary: "The package summary",
    });

});
