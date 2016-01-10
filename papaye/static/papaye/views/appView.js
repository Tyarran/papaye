define('views/appView', [], function() {
    'use strict';

    return Backbone.View.extend({
        el: 'head',

        initialize: function() {
            this.title = $("title");
            this.originalTitle = this.title.html();
        },

        render: function() {
            this.title.html(this.originalTitle + " -  Mon Titre");
        }
    });
});
