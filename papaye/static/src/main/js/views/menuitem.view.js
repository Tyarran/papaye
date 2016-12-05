import Marionette from 'backbone.marionette';
import Handlebars from 'handlebars';

import MenuItemModel from '../models/menuitem.model';
import MenuItemTemplate from '../../templates/menuitem.template.html!text';


const MenuItemView = Marionette.ItemView.extend({
    template: Handlebars.compile(MenuItemTemplate),
    model: MenuItemModel,
    tagName: 'li',

    className() {
        return this.model.get('active');
    },
});

export default MenuItemView;
