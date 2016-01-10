define('collections/PackageSummaryCollection', ['common', 'models/PackageSummary'], function(common, PackageSummary){

    return Backbone.Collection.extend({
        url: "/api/package/json",
        model: PackageSummary,

        parse: function(response, options) {
            return response.result;
        }
    });
});
