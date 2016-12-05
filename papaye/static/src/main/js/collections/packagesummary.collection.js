import Backbone from 'backbone';

import PackageSummaryModel from '../models/packagesummary.model';


var PackageSummaryCollection = Backbone.Collection.extend({
    model: PackageSummaryModel,
    url: window.APP_CONTEXT.urls.package_resource,

    parse(response) {
        return response.result;
    }
});

export default PackageSummaryCollection;
