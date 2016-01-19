var dependencies = [
    'common',
    'views/ContentView',
    'views/ListPackageView',
    'views/LoginView',
    'views/ReleaseDetailView',
    'views/BreadcrumsView',
    'collections/Breadcrumb',
    'models/Registry',
];

define('routers/appRouter', dependencies, function(common, ContentView, ListPackageView, LoginView, ReleaseDetailView, BreadcrumsView, Breadcrumb, registry) {
    'use strict';

    return Backbone.Router.extend({

        routes: {
            "": "home", // url:event that fires
            "browse": "browse", // url:event that fires
            "browse/:packageName": "releaseDetail",
            "browse/:packageName/:version": "releaseDetail",
            "login/*path": "login",
        },

        routeWithoutBreadcrumbs: [
            'login',
        ],

        initialize: function(el) {
            this.el = el;
            this.openViews = ['homeView', 'loginView'];

            this.on('route', this.buildBreadcrumb, this);
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
            var fragment = Backbone.history.getFragment();

            if (_.indexOf(this.openViews, view.name) === -1) {
                $.get(registry.get('server_vars')['is_logged_url'])
                .done(function(response) {
                    registry.set('username', response)
                    doSwitch.apply(self);
                })
                .fail(function(error) {
                    if (error.status === 401) {
                        registry.get('router').navigate('//login/' + fragment);
                        registry.set('username', null)
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

        buildBreadcrumb: function(route) {
            var fragment = Backbone.history.getFragment();
            var breadcrumbs = registry.get('breadcrumbs');
            var items = [{
                href: '#/',
                name: '<i class="glyphicon glyphicon-home"></i>',
            }];
            var lastItem = null;

            _.each(fragment.split('/'), function(fragmentPart) {
                if (fragmentPart !== '') {
                    items.push({
                        href: '#/' + fragment.split(fragmentPart)[0] + fragmentPart,
                        name: fragmentPart,
                    });
                }
            });

            lastItem = _.last(items);
            lastItem.active = true;
            items[items.length - 1] = lastItem;

             
            breadcrumbs.reset();
            if (_.contains(this.routeWithoutBreadcrumbs, route) == false) {
                breadcrumbs.add(items);
            }
        },

        home: function() {
            registry.get('activePage').set({name: 'home'});

            this.switchView(new ContentView({
                template: '#index_tmpl',
                name: 'homeView',
            }));
            $('pre').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        browse: function() {
            registry.get('activePage').set({name: 'browse'});
            this.switchView(new ListPackageView({
                template: '#list_packages_tmpl',
                name: 'listPackagesView',
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

            registry.get('activePage').set({name: 'browse'});
            //BreadcrumsView.items.reset();
            this.switchView(new ReleaseDetailView( context));
        }, 

        login: function(path) {
            this.switchView(new LoginView({template: '#login_tmpl', name: 'loginView', path: path}));
        }
    });
});
