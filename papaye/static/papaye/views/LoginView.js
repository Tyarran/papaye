define('views/LoginView', ['common', 'handlebars', 'views/ContentView', 'text!partials/login.html'], function(common, Handlebars, ContentView, template){

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

            console.log(app.server_vars['login_route_url']);
            $.ajax({
                url: app.server_vars['login_route_url'],
                method: 'post',
                data: {username: 'admin', password: 'admin'},
                dataType: 'json',
                context: this.path,
            })
            .done(function(response) {
                app.router.navigate('//' + this);
            })
            .error(function(error) {
                console.log(error.status)
                console.log('Pas logué', error);
            });
        },

    });
});
