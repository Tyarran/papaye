import Marionette from 'backbone.marionette';
import Handlebars from 'handlebars';

import NavbarView from './navbar.view';
import BreadcrumbView from './breadcrumb.view';

import appTemplate from '../../templates/app.template.html!text';

import 'bootstrap/dist/css/bootstrap.css!';
import 'ubuntu-fontface/ubuntu.css!';
import 'font-awesome/css/font-awesome.min.css!';


const AppView = Marionette.LayoutView.extend({
    template: Handlebars.compile(appTemplate),

    ui: {
        navbar: '.navbar-placeholder',
        content: '.content-placeholder',
        breadcrumb: '.breadcrumb-placeholder',
    },

    regions: {
        navbar: '@ui.navbar',
        content: '@ui.content',
        breadcrumb: '@ui.breadcrumb',
    },

    initialize(options) {
        console.log(options);
        this.router = options.router

        this.listenTo(this.router, 'route:changed', this.onRouteChanged); 
    },

    onRender() {
        this.navbar.show(new NavbarView({router: this.router}));
        this.breadcrumb.show(new BreadcrumbView({router: this.router}));
    },

    onRouteChanged(view) {
        this.content.show(view);
        // firefox
        $('html').scrollTop(0);
        // chrome/chromium
        $('body').scrollTop(0);
        console.log(this.ui.html);
    }

});

export default AppView;
