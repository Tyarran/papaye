define('models/Registry', ['common'], function(common) {
    var Registry = Backbone.Model.extend({
        defaults: {
            username: null,
            server_vars: null,
            activePage: null,
            router: null,
            breadcrumbs: null,
        }
    });
    return new Registry();
});
