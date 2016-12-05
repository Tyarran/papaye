import 'bootstrap';
import Handlebars from 'handlebars';
import Marionette from 'backbone.marionette';
import _ from 'underscore';
import hljs from 'highlightjs';

import PackageDetailTemplate from '../../templates/packagedetail.template.html!text';


const PackageDetailView = Marionette.ItemView.extend({
  template: Handlebars.compile(PackageDetailTemplate),

  ui: {
    codeBlocks: 'pre.literal-block',
    tabLinks: 'ul.nav.nav-tabs a'
  },

  events: {
    'click @ui.tabLinks': 'onTabClick',
  },

  templateHelpers() {
      return {
          hashOtherReleases: this.model.get('other_releases').length === 0,
      }
  },

  onTabClick(event) {
    event.preventDefault();

    $(event.currentTarget).tab('show');
  },

  onDomRefresh() {
    _.each(this.ui.codeBlocks, (block) => {
      hljs.highlightBlock(block);
    });
  }

});

export default PackageDetailView;
