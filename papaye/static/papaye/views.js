var app = app || {};

(function($) {
    'use strict';

    app.appView = Backbone.View.extend({
        el: 'head',

        initialize: function() {
            this.title = $("title");
            this.originalTitle = this.title.html();

            this.render();
        },

        render: function() {
            this.title.html(this.originalTitle + " -  Mon Titre");
        }
    });

    app.NavView = Backbone.View.extend({
        el: '#navbar',

        events: {
            'click ul[role=tablist] a': 'changeActivePage',
        },

        initialize: function() {
            this.pageUI = $('ul[role=tablist]');
            this.pages = ["home", "browse"];
            this.li = this.pageUI.find('li');
            this.pages = new app.PageCollection([
                {name: 'home', url: '#/'},
                {name: 'browse', url: '#/browse'}
            ]);
            this.test_tmpl = _.template($('#test_tmpl').html());
            this.activePage = this.pages.at(0);

            this.render();
            this.li = this.pageUI.find('li');
        },

        tablistClick: function(event) {
            var pageName = $(event.target).data('name');
            
            this.changeActivePage(pageName);
        },

        changeActivePage: function(pageName) {
            var activePage = undefined;

            _.each(this.li, function(li) {
                var $li = $(li);
                var $a = $li.find('a');

                if ($a.data('name') !== pageName) {
                    $li.removeClass('active');
                }
                else {
                    $li.addClass('active');
                    activePage = pageName;
                }
            });
            this.activePage = activePage;
        },

        render: function() {
            this.pageUI.empty();
            this.pages.each(function(page) {
                var context = {
                    name: page.get('name'),
                    url: page.get('url'),
                    active: (page.get('name') === this.view.activePage.get('name'))? 'active': '',
                }
                this.view.pageUI.append(this.view.test_tmpl(context))
            }, {view: this});
        }
    });

    app.ContentView = Backbone.View.extend({

        initialize: function(options) {
            this.template = _.template($(options.template).html());
        },

        render: function() {
            var content = this.template(app.server_vars);

            $(this.el).html(content);
            return this;
        }
    });

    app.ListPackageView = app.ContentView.extend({

        initialize: function(options) {
            this.template = _.template($(options.template).html());
            this.packageSummaries = new app.PackageSummaryCollection();
            this.row_tmpl = _.template($('#list_package_row').html());

            this.packageSummaries.on('sync', function(event) {this.view.render()}, {view: this});
            this.packageSummaries.fetch();
        },

        render: function(event) {
            var context = app.server_vars; 
            var content = undefined;

            context.packageCount = this.packageSummaries.length;
            content = this.template(context);

            $(this.el).html(content);
            this.packageSummaries.each(function(packageSummary) {
               $('#package_list').append(this.view.row_tmpl({package: packageSummary}));
            }, {"view": this});
            return this;
        }
    });
})(jQuery);
