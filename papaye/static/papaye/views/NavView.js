var dependencies = [
    'common',
    'handlebars',
    'collections/PageCollection',
    'text!partials/navview.html',
    'models/Registry',
];

define('views/NavView', dependencies, function (common, Handlebars, PageCollection, template, registry) {
    return Backbone.View.extend({
        el: '#navbar',

        events: {
            'click #logout': 'logout',
            'click #login-btn': 'login',
        },

        initialize: function() {
            this.pageUI = $('ul[role=tablist]');
            this.pages = ["home", "browse"];
            this.li = this.pageUI.find('li');
            this.pagesCollection = new PageCollection([
                {name: 'Home', url: '#/'},
                {name: 'Browse', url: '#/browse'}
            ]);
            this.test_tmpl = Handlebars.compile(template);
            this.activePage = registry.get('activePage');

            this.activePage.on('change:name', this.render, this);
            registry.on('change:username', this.render, this);
        },

        logout: function(event) {
            $.get(registry.get('server_vars').logout_route_url, function(data) {
                Backbone.history.stop();
                Backbone.history.start();
            });
            this.render();
            noty({text: 'You are now disconnected', type: "success", layout: "bottom", timeout: 5000});
        },

        login: function(event) {
            event.preventDefault();
            registry.get('router').navigate('//login/browse');
        },

        render: function() {
            var context = {pages: [], username: registry.get('username')};

            this.pagesCollection.each(function(page) {
                var page = {
                    name: page.get('name'),
                    url: page.get('url'),
                    active: (page.get('name') === this.activePage.get('name'))? 'active': '',
                }
                context.pages.push(page);
            }, this);
            this.$el.html(this.test_tmpl(context));
            this.li = this.pageUI.find('li');
        }
    });
});
