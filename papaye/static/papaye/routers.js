var app = app || {};

(function() {
    'use strict';

    app.appRouter = Backbone.Router.extend({

        routes: {
            "": "home", // url:event that fires
            "browse": "browse", // url:event that fires
            "browse/:packageName": "releaseDetail",
        },

        initialize: function(el) {
            this.el = el;
        },


        notifyActivePageChange: function(page) {
            app.navView.changeActivePage(page);
        },

        switchView: function(view) {
            if (this.currentView) {
                // Detach the old view
                this.currentView.remove();
            }

            // Move the view element into the DOM (replacing the old content)
            this.el.html(view.el);

            // Render view after it is in the DOM (styles are applied)
            view.render();

            this.currentView = view;
        },

        redirectToHome: function() {
            this.navigate("//");
        },

        home: function() {
            this.notifyActivePageChange('home');
            this.switchView(new app.ContentView({template: '#index_tmpl'}));
            $('pre').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        browse: function() {
            this.notifyActivePageChange('browse');
            this.switchView(new app.ListPackageView({template: '#list_packages_tmpl'}));
        },

        releaseDetail: function(packageName) {
            this.notifyActivePageChange('browse');
            this.switchView(new app.ReleaseDetailView({
                template: '#package_detail_tmpl',
                packageName: packageName,
            }));
        }, 
    });
})();
