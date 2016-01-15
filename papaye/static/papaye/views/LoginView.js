define('views/LoginView', ['common', 'handlebars', 'views/ContentView', 'text!partials/login.html', 'models/Registry'], function(common, Handlebars, ContentView, template, registry){

    return ContentView.extend({

         events: {
             'click button[type=submit]': 'formSubmit',
         },

        initialize: function(options) {
            this.template = Handlebars.compile(template);
            this.name = options.name;
            this.path = options.path;
        },

        formSubmit: function(event) {
            event.preventDefault();

            $.ajax({
                url: registry.get('server_vars')['login_route_url'],
                method: 'post',
                data: {username: 'admin', password: 'admin'},
                dataType: 'json',
                context: this.path,
            })
            .done(function(response) {
                registry.get('router').navigate('//' + this);
                noty({text: 'You are now connected', type: "success", layout: "bottom", timeout: 5000});
            })
            .error(function(error) {
                noty({text: 'Identification failed', type: "error", layout: "bottom", timeout: 5000});
            });
        },

    });
});
