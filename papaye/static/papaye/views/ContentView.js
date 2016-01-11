define('views/ContentView', ['common', 'handlebars', 'text!partials/index.html' ], function(common, Handlebars, template) {
    return Backbone.View.extend({

        initialize: function(options) {
            this.template = Handlebars.compile(template)
            this.name = options.name;
            options.breadcrumbs.add({
                href: '#/',
                name: '<i class="glyphicon glyphicon-home"></i>',
                active: true,
            });
        },

        render: function() {
            var content = this.template(app.server_vars);

            $(this.el).html(content);
            return this;
        }
    });
});
