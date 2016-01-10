define('models/Release', ['common', ], function() {

    return Backbone.Model.extend({
        
        initialize: function(options) {
            this.name = options.packageName;
            this.version = options.version;
        },

        url: function() {
            var url = '/api/package/' + this.name + '/json';

            if (this.version !== undefined && this.version !== null) {
                url = '/api/package/' + this.name + '/' + this.version + '/json'
            }
            return url;
        },
    });

});
