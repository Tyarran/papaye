import 'bootstrap';
import Backbone from 'backbone';
import Marionette from 'backbone.marionette';

import MenuItemCollection from '../collections/menuitem.collection';
import MenuItemView from './menuitem.view';
import navbarTemplate from '../../templates/navbar.template.html!text';

const NavbarView = Marionette.CompositeView.extend({
    template: Handlebars.compile(navbarTemplate),

    ui: {
        menu: '.menu-placeholder',
        logout: '.logout',
    },

    events: {
        'click @ui.logout': 'onLogout',
    },

    childView: MenuItemView,

    childViewContainer: '@ui.menu',

    templateHelpers: {
        username: window.APP_CONTEXT.username,
    },

    onLogout() {
        Backbone.ajax(window.APP_CONTEXT.urls.logout).done(() => {
            window.location = window.APP_CONTEXT.urls.login;
        });
    },

    initialize(options) {
        this.options = options;
        this.router = options.router;
        this.collection = new MenuItemCollection([{
            name: 'home',
            label: 'Home',
            url: '#/home',
            active: 'active',
        }, {
            name: 'browse',
            label: 'Browse packages',
            url: '#/browse',
            active: '',
        }]);

        this.listenTo(this.router, 'route:changed', this.onRouteChange);
    },

    onRouteChange(view, routeName) {
        const tmp = [];
        this.collection.each((item) => {
            if (item.get('name') === routeName) {
                item.set('active', 'active');
            } else {
                item.set('active', '');
            }
            tmp.push(item);
        })
        this.collection.reset(tmp);
    },

});

export default NavbarView;
