var dependencies = [
    'common',
    'views/ContentView',
    'views/ListPackageView',
    'views/LoginView',
    'views/ReleaseDetailView',
    'views/BreadcrumsView',
    'collections/Breadcrumb'
];

define('routers/appRouter', dependencies, function(common, ContentView, ListPackageView, LoginView, ReleaseDetailView, BreadcrumsView, Breadcrumb) {
    'use strict';

    var breadcrumbs = {
       home: {
           href: '#/',
           name: 'home',
       },
       browse: {
           href: '#/browse',
           name: 'browse',
       },
       releaseDetail: {
           href: '#/browse',
           name: 'browse',
       }
    };

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
            this.currentBreadcrums = [];
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
            var homeBreadcrumb = {};

            _.extend(homeBreadcrumb, breadcrumbs.home);
            app.activePage.set({name: 'home'});
            BreadcrumsView.items.reset();
            this.switchView(new ContentView({
                template: '#index_tmpl',
                name: 'homeView',
                breadcrumbs: BreadcrumsView.items,
            }));
            this.currentBreadcrums = [homeBreadcrumb];
            $('pre').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        browse: function() {
            app.activePage.set({name: 'browse'});
            BreadcrumsView.items.reset();
            this.switchView(new ListPackageView({
                template: '#list_packages_tmpl',
                name: 'listPackagesView',
                breadcrumbs: BreadcrumsView.items,
            }));
        },

        releaseDetail: function(packageName, version) {
            var context = {
                template: '#package_detail_tmpl',
                packageName: packageName,
                version: version,
                name: 'releaseDetailView',
                breadcrumbs: BreadcrumsView.items,
            }

            app.activePage.set({name: 'browse'});
            BreadcrumsView.items.reset();
            this.switchView(new ReleaseDetailView( context));
        }, 

        login: function(path) {
            this.switchView(new LoginView({template: '#login_tmpl', name: 'loginView', path: path}));
        }
    });
});
