var app = app || {};

(function(){
    'use strict';

    app.PageCollection = Backbone.Collection.extend({
        model: app.Page,
    });
})();
