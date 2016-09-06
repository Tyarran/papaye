import Backbone from 'backbone';


const PackageModel = Backbone.Model.extend({
  url() {
      const name = this.get('name');
      const version = this.get('version');
      if (version) {
          return `${window.APP_CONTEXT.urls.api}package/${name}/${version}/json`;
      }
      else {
          return `${window.APP_CONTEXT.urls.api}package/${name}/json`;
      }
  },
});


export default PackageModel;
