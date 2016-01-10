define('collections/PageCollection', ['common', 'models/Page'], function(common, Page){

    return Backbone.Collection.extend({
        model: Page,
    });

});
