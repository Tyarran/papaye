import Handlebars from 'handlebars';
import Marionette from 'backbone.marionette';


import BreadcrumbItemTemplate from '../../templates/breadcrumbitem.template.html!text';


const BreadcrumbItemView = Marionette.ItemView.extend({
  template: Handlebars.compile(BreadcrumbItemTemplate),

  tagName: 'li',

  className() {
    let result = '';
    if (this.model.get('active') === true) {
      result = 'active';
    }
    return result;
  }
});


export default BreadcrumbItemView;
