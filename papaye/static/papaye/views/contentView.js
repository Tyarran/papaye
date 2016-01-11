define('views/ContentView', ['handlebars'], function(Handlebars) {
    return Backbone.View.extend({

        initialize: function(options) {
            this.template = Handlebars.compile($(options.template).html())
            this.name = options.name;
        },

        render: function() {
            var content = this.template(app.server_vars);

            $(this.el).html(content);
            return this;
        }
    });
});
