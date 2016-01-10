var dependencies = [
    'common',
    'views/ContentView',
    'views/ListPackageView',
    'views/LoginView',
    'views/ReleaseDetailView'
];

define('routers/appRouter', dependencies, function(common, ContentView, ListPackageView, LoginView, ReleaseDetailView) {
    'use strict';

    return Backbone.Router.extend({

        routes: {
            "": "home", // url:event that fires
            "browse": "browse", // url:event that fires
            "browse/:packageName": "releaseDetail",
            "browse/:packageName/:version": "releaseDetail",
            "login/*path": "login",
        },

        initialize: function(el) {
            this.el = el;
            this.openViews = ['homeView', 'loginView'];
        },


        switchView: function(view) {
            var doSwitch = function() {
                if (this.currentView) {
                    // Detach the old view
                    this.currentView.remove();
                }

                // Move the view element into the DOM (replacing the old content)
                this.el.html(view.el);

                // Render view after it is in the DOM (styles are applied)
                view.render();

                this.currentView = view;
            };
            var self = this;

            if (_.indexOf(this.openViews, view.name) === -1) {
                $.get(app.server_vars['is_logged_url'])
                .done(function(response) {
                    doSwitch.apply(self);
                })
                .fail(function(error) {
                    console.log(error);
                    if (error.status === 401) {
                        app.router.navigate('//login/browse');
                    }
                });
            }
            else {
                doSwitch.apply(this);
            }
        },

        redirectToHome: function() {
            this.navigate("//");
        },

        home: function() {
            app.activePage.set({name: 'home'});
            this.switchView(new ContentView({template: '#index_tmpl', name: 'homeView'}));
            $('pre').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        browse: function() {
            app.activePage.set({name: 'browse'});
            this.switchView(new ListPackageView({template: '#list_packages_tmpl', name: 'listPackagesView'}));
        },

        releaseDetail: function(packageName, version) {
            var context = {
                template: '#package_detail_tmpl',
                packageName: packageName,
                version: version,
                name: 'releaseDetailView',
            }

            app.activePage.set({name: 'browse'});
            this.switchView(new ReleaseDetailView(context));
        }, 

        login: function(path) {
            this.switchView(new LoginView({template: '#login_tmpl', name: 'loginView', path: path}));
        }
    });
});
