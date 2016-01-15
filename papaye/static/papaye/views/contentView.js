define('views/ContentView', ['handlebars', 'models/Registry'], function(Handlebars, registry) {
    return Backbone.View.extend({

        initialize: function(options) {
            this.template = Handlebars.compile($(options.template).html())
            this.name = options.name;
        },

        render: function() {
            var content = this.template(registry.get('server_vars'));

            $(this.el).html(content);
            return this;
        }
    });
});
