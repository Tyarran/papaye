import Backgrid from 'backgrid';
import Handlebars from 'handlebars';
import Marionette from 'backbone.marionette';

import ListPackageTemplate from '../../templates/listpackage.template.html!text';
import PackageSummaryCollection from '../collections/packagesummary.collection';

import 'backgrid/lib/backgrid.css!';


Backgrid.PackagelinkCell = Backgrid.Cell.extend({
  tagName: 'td',
  className: "package-link-cell",
  formatter: Backgrid.StringFormatter,

  render() {
    this.$el.html(`<a href="${this.model.detailUrl()}">${this.model.get('name')}</a>`);
    return this;
  }
});



const ListPackageView = Marionette.LayoutView.extend({
    template: Handlebars.compile(ListPackageTemplate),

    ui: {
        listPackage: '.list-placeholder',
        resetFilterBtn: '.reset-filter',
        filterInput: 'input.filter',
        packageCount: '.package-count'
    },

    regions: {
        listPackage: '@ui.listPackage',
    },

    events: {
        'click @ui.resetFilterBtn': 'resetFilterBtnClick',
        'keyup @ui.filterInput': 'onFilterInputKeyUp',
    },

    initialize() {
        this.collection = new PackageSummaryCollection();
        this.packageSummaries = new PackageSummaryCollection();
        this.grid = new Backgrid.Grid({
            columns: [{
                name: 'name',
                label: 'Name',
                cell: 'packagelink',
                editable: false,
            }, {
                name: 'summary',
                label: 'Summary',
                cell: 'string',
                editable: false,
            }],
            collection: this.collection,
        });

        this.listenTo(this.collection, 'update', this.renderGrid);
        this.listenTo(this.packageSummaries, 'update', this.synchronizeCollection);
    },

    onFilterInputKeyUp(event) {
        const filterValue = this.ui.filterInput.val();

        const result = this.packageSummaries.filter((packageSummary) => {
            return packageSummary.get('name').startsWith(filterValue);
        });
        this.collection.reset(result);
    },

    renderGrid() {
        this.listPackage.show(this.grid);
        this.ui.packageCount.text(this.collection.length);
    },

    resetFilterBtnClick() {
        this.ui.filterInput.val(null);
        this.collection.reset(this.packageSummaries.models);
    },

    onShow() {
        this.packageSummaries.fetch();
    },

    synchronizeCollection(collection) {
        this.collection.add(collection.models)
    },
});

export default ListPackageView;
