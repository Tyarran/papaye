var dependencies = [
    'common',
    'handlebars',
    'views/ContentView',
    'models/Release', 
    'text!partials/package.html',
    'text!partials/loading.html',
    'text!partials/error.html',
];

define('views/ReleaseDetailView', dependencies, function(common, Handlebars, ContentView, Release, template, loadingTemplate, errorTemplate) {

    return ContentView.extend({

        events: {
            "click a[role=tab]": 'tab',
        },

        initialize: function(options) {
            this.name = options.name;
            this.loadingTemplate = Handlebars.compile(loadingTemplate);
            this.template = Handlebars.compile(template);
            this.release = new Release(options);

            this.release.on('sync', this.renderRelease, this);
        },

        renderRelease: function(event) {
            var content = this.template({release: this.release.toJSON()});

            this.$el.html(content);
            this.$el.find('pre.literal-block').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        },

        error: function(event) {
            var $el = $(this.el);

            $el.html(errorTemplate);
            console.log(this.errorTemplate);
        },

        tab: function(event) {
            var $TabLiNodes = $("#download-tab>li");
            var $currentTabNode = $(event.target).parent();
            var $tabpane = $($currentTabNode.find('a').data('toggle'));

            event.preventDefault(); // Remove defaults actions

            // Reset all tab pane
            $("#download_link .tab-pane").hide();
            $TabLiNodes.removeClass('active');

            $currentTabNode.addClass('active');
            $tabpane.show();
        },

        render: function() {
            var $el = $(this.el);

            this.release.fetch({error: this.error, context: this});
            var content = this.loadingTemplate({package: this.release.name});
            $el.html(content);
            return this;
        },
    });
});
