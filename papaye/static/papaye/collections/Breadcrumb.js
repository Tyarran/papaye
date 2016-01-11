define('collections/Breadcrumb', ['common', 'models/BreadcrumbItem'], function(common, BreadcrumbItem) {
    return Backbone.Collection.extend({
        model: BreadcrumbItem
    });
});
