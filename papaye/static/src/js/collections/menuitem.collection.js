import Backbone from 'backbone';

import MenuItemModel from '../models/menuitem.model';


const MenuItemCollection = Backbone.Collection.extend({
    model: MenuItemModel,
});

export default MenuItemCollection;
