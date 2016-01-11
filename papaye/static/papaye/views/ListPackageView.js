var dependencies = [
    'common',
    'handlebars',
    'collections/PackageSummaryCollection',
    'views/ContentView',
    'text!partials/list_packages.html',
    'text!partials/list_package_row.html',
];

define('views/ListPackageView', dependencies, function(common, Handlebars, PackageSummaryCollection, ContentView, template, row_template) {

    return ContentView.extend({

        events: {
            "keyup #search_input": "filterValueChanged",
            "click #remove_filter": "resetFilter",
        },

        initialize: function(options) {
            this.template = Handlebars.compile(template);
            this.name = options.name;
            this.packageSummaries = new PackageSummaryCollection();
            this.row_tmpl = Handlebars.compile(row_template);
            
            this.packageSummaries.on('sync', function() {this.filterList()}, this);
            this.packageSummaries.fetch();
            options.breadcrumbs.add([{
                href: '#/',
                name: '<i class="glyphicon glyphicon-home"></i>',
            }, {
                href: '#/browse',
                name: 'browse',
                active: true,
            }]);

            this.attrEvent = {};
            _.extend(this.attrEvent, Backbone.Events);

            this.attrEvent.on('filterValue:change', function(filterValue) {
                this.filterList(filterValue);
            }, this);
        }, 

        filterValueChanged: function(event) {
            var value = $(event.target).val();
            
            this.attrEvent.trigger('filterValue:change', value);
        },

        filterList: function(filterValue) {
            var packageCount = this.packageSummaries.length;
            var $packageList = $('#package_list');
            $packageList.empty();

            this.packageSummaries.each(function(packageSummary, index) {
                var url = "#/browse/" + packageSummary.get('name');

                if (filterValue === undefined || packageSummary.get('name').toLowerCase().startsWith(filterValue.toLowerCase())) {
                    $packageList.append(this({
                        package: packageSummary.toJSON(),
                        index: index,
                        url: url,
                    }));
                }
            }, this.row_tmpl);
            $("#package_count").text(packageCount + " packages");
        },

        resetFilter: function(event) {
            var $searchInput = $("#search_input");

            $searchInput.val('');
            this.packageSummaries.fetch();
        },

        viewPackageDetails: function(event) {
            var $element = $(event.target).parent();
            var index = $element.data('index');
            var packageSummary = this.packageSummaries.at(index);

            app.router.navigate("//browse/" + packageSummary.get('name'));
        },

        render: function() {
            var context = {
                packageCount: this.packageSummaries.length,
                filterValue: this.filterValue,
            }

            this.packageSummaries.fetch();

            $(this.el).html(this.template(context));
            return this;
        }
    });
});
