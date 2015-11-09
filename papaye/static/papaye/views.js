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
            'click ul[role=tablist] li': 'tablistClick',
        },

        initialize: function() {
            this.pageUI = $('ul[role=tablist]');
            this.pages = ["home", "browse"];
            this.li = this.pageUI.find('li');
            this.pagesCollection = new app.PageCollection([
                {name: 'home', url: '#/'},
                {name: 'browse', url: '#/browse'}
            ])
            this.test_tmpl = Handlebars.compile($('#test_tmpl').html());
            this.activePage = this.pagesCollection.at(0);
            this.render();
        },

        tablistClick: function(event) {
            var pageName = $(event.target).data('name');

            this.changeActivePage(pageName);
        },

        changeActivePage: function(pageName) {
            this.activePage = this.pagesCollection.findWhere({name: pageName})
            this.render();
        },

        render: function() {
            var context = {pages: []};

            this.pagesCollection.each(function(page) {
                var page = {
                    name: page.get('name'),
                    url: page.get('url'),
                    active: (page.get('name') === this.view.activePage.get('name'))? 'active': '',
                }
                context.pages.push(page);
            }, {view: this});
            this.$el.html(this.test_tmpl(context));
            this.li = this.pageUI.find('li');
        }
    });

    app.ContentView = Backbone.View.extend({

        initialize: function(options) {
            this.template = Handlebars.compile($(options.template).html())
        },

        render: function() {
            var content = this.template(app.server_vars);

            $(this.el).html(content);
            return this;
        }
    });

    app.ListPackageView = app.ContentView.extend({

        events: {
            "keyup #search_input": "filterList",
            "click #remove_filter": "resetFilter",
        },

        initialize: function(options) {
            this.template = Handlebars.compile($(options.template).html());
            this.packageSummaries = new app.PackageSummaryCollection();
            this.row_tmpl = Handlebars.compile($('#list_package_row').html());

            this.packageSummaries.on('sync', this.filterList, this);
            this.packageSummaries.fetch();
        },

        filterList: function(event) {
            var filterInput = $(event.target);
            var filterValue = filterInput.val();
            var filteredResult = undefined;
                
            if (filterValue !== '' && filterValue !== undefined) {
                filteredResult = this.packageSummaries.filter(function(packageSummary) {
                    return packageSummary.get('name').startsWith(filterValue) }
                );
            }
            else {
                filteredResult = this.packageSummaries.filter(function(packageSummary) {
                    return true === true }
                );
            }

            this.fillPackageSummaryList(filteredResult);
        },

        resetFilter: function(event) {
            var $searchInput = $("#search_input");

            $searchInput.val('');
            this.fillPackageSummaryList(this.packageSummaries.filter(function(packageSummary) { return 1 === 1 }));
        },

        viewPackageDetails: function(event) {
            var $element = $(event.target).parent();
            var index = $element.data('index');
            var packageSummary = this.packageSummaries.at(index);

            app.router.navigate("//browse/" + packageSummary.get('name'));
        },

        fillPackageSummaryList: function(filteredPackageSummaries) {
            var packageCount = filteredPackageSummaries.length;
            var $packageList = $('#package_list');

            $packageList.empty();

            _.each(filteredPackageSummaries, function(packageSummary, index) {
                var url = "#/browse/" + packageSummary.get('name');

                $packageList.append(this.view.row_tmpl({
                    package: packageSummary.toJSON(),
                    index: index,
                    url: url,
                }));
            }, {"view": this});
            $("#package_count").text(packageCount + " packages");
        },

        render: function() {
            var context = {packageCount: this.packageSummaries.length}

            console.log(context.packageCount);
            $(this.el).html(this.template(context));
            return this;
        }
    });

    app.ReleaseDetailView = app.ContentView.extend({

        events: {
            "click a[role=tab]": 'tab',
        },

        initialize: function(options) {
            this.template = Handlebars.compile($(options.template).html());
            this.loadingTemplate = Handlebars.compile($('#package_detail_loading_tmpl').html());
            this.packageName = options.packageName;
            this.release = new app.Release(this.packageName);
            this.release.on('sync', function(event) {this.view.render(true)}, {view: this});
            this.release.fetch();
        },

        tab: function(event) {
            var $TabLiNodes = $("#download-tab>li");
            var $currentTabNode = $(event.target);

            event.preventDefault(); // Remove defaults actions

            _.each($TabLiNodes, function(element) {
                var element = $(element);

                element.removeClass('active');
            });

            $currentTabNode.addClass('active');
        },

        render: function(sync) {
            var $el = $(this.el);
            if (sync) {
                console.log(this.release.attributes);
                var content = this.template({release: this.release.toJSON()});

                $el.html(content);
                $el.find('pre.literal-block').each(function(i, block) {
                   hljs.highlightBlock(block);
                });
            }
            else {
                var content = this.loadingTemplate();
                $el.html(content);
            }
            return this;

        },
    });
})(jQuery);
