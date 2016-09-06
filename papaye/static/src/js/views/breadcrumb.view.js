import Backbone from 'backbone';
import Handlebars from 'handlebars';
import Marionette from 'backbone.marionette';

import BreadcrumbItemView from './breadcrumbitem.view';


const BreadcrumbView = Marionette.CollectionView.extend({
  childView: BreadcrumbItemView,
  tagName: 'ol',
  className: 'breadcrumb',

  initialize(options) {
    this.router = options.router;
    this.collection = new Backbone.Collection(); 
    this.listenTo(this.router, 'route:changed', this.onRouteChange);
  },

  onRouteChange(view, routeName, breadcrumbItems) {
    console.log('routeChange');
    console.log(breadcrumbItems);
    this.collection.reset(breadcrumbItems);
  },

});

export default BreadcrumbView;
