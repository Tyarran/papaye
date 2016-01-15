define('views/ContentView', ['common', 'handlebars', 'text!partials/index.html', 'models/Registry' ], function(common, Handlebars, template, registry) {
    return Backbone.View.extend({

        initialize: function(options) {
            this.template = Handlebars.compile(template)
            this.name = options.name;
        },

        render: function() {
            var content = this.template(registry.get('server_vars'));

            $(this.el).html(content);
            return this;
        }
    });
});
