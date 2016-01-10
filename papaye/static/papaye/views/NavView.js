define('views/NavView', ['common', 'handlebars', 'collections/PageCollection'], function (common, Handlebars, PageCollection) {

    return Backbone.View.extend({
        el: '#navbar',

        initialize: function() {
            this.pageUI = $('ul[role=tablist]');
            this.pages = ["home", "browse"];
            this.li = this.pageUI.find('li');
            this.pagesCollection = new PageCollection([
                {name: 'home', url: '#/'},
                {name: 'browse', url: '#/browse'}
            ])
            this.test_tmpl = Handlebars.compile($('#test_tmpl').html());

            app.activePage.on('change:name', this.changeActivePage, this);
        },

        changeActivePage: function(page) {
            this.render();
        },

        render: function() {
            var context = {pages: []};

            this.pagesCollection.each(function(page) {
                var page = {
                    name: page.get('name'),
                    url: page.get('url'),
                    active: (page.get('name') === app.activePage.get('name'))? 'active': '',
                }
                context.pages.push(page);
            });
            this.$el.html(this.test_tmpl(context));
            this.li = this.pageUI.find('li');
        }
    });
});
