import Backbone from 'backbone';


const PackageSummaryModel = Backbone.Model.extend({
  detailUrl() {
    return `#/browse/${this.get('name')}`;
  }
});


export default PackageSummaryModel;
