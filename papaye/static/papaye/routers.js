var app = app || {};

(function() {
    'use strict';

    app.appRouter = Backbone.Router.extend({

        routes: {
            "": "home", // url:event that fires
            "browse": "browse", // url:event that fires
        },

        initialize: function(el) {
            this.el = el;
            this.homeView = new app.ContentView({template: '#index_tmpl'});
            this.ListPackageView = new app.ListPackageView({template: '#list_packages_tmpl'});
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
            this.switchView(this.homeView);
            $('pre code').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        browse: function() {
            this.notifyActivePageChange('browse');
            this.switchView(this.ListPackageView);
        },
    });
})();
