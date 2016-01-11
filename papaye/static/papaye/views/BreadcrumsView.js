define("views/BreadcrumsView", ['common', 'handlebars', 'text!partials/breadcrums.html', 'collections/Breadcrumb'], function(common, Handlebars, elementTemplate, Breadcrumb) {
    var instance = null;
    var BreadcrumbView = Backbone.View.extend({
        el: '#breadcrumb',

        initialize: function(options) {
            this.elementTemplate = Handlebars.compile(elementTemplate);
            this.template = Handlebars.compile('<ol class="breadcrumb"></ol>');
            this.items = new Breadcrumb();

            this.listenTo(this.items, 'update', this.updateBreadcrumb);

            this.render();
        },

        updateBreadcrumb: function(event) {
            this.$breadcrumb.empty();

            this.items.each(function(item) {
                var content = this.elementTemplate(item.toJSON());

                this.$breadcrumb.append(content)
            }, this);
        },

        render: function() {
            var content = this.template();

            this.$el.append(content);
            this.$breadcrumb = this.$el.find('ol.breadcrumb');
            return this;
        }
    });

    if (instance === null){
        console.log(BreadcrumbView);
        instance = new BreadcrumbView();
    }
    return instance;
});
