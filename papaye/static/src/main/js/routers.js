import Backbone from 'backbone';

import IndexView from './views/index.view';
import ListPackageView from './views/listpackage.view';
import PackageDetailView from './views/packagedetail.view';
import PackageModel from './models/package.model';


const AppRouter = Backbone.Router.extend({
    routes: {
        '': 'redirectToHome',
        'home': 'home',
        'browse/:packageName': 'detail',
        'browse/:packageName/:version': 'detail',
        'browse': 'browse',
    },

    redirectToHome() {
        this.navigate('//home')
    },

    home() {
        this.trigger('route:changed', new IndexView(), 'home', [{
          name: '<i class="fa fa-home"></i>',
          url: '#/',
          active: true,
        }]);
    },

    browse() {
        this.trigger('route:changed', new ListPackageView(), 'browse', [{
          name: '<i class="fa fa-home"></i>',
          url: '#/',
        }, {
          name: 'Browse packages',
          url: '#/browse',
          active: true,
        }]);
    },

    detail(packageName, version) {
      const model = new PackageModel({ name: packageName, version: version });
      Promise.resolve(model)
        .then((model) => {
          return model.fetch();
      })
        .then((result) => {
            this.trigger('route:changed', new PackageDetailView({ model: new PackageModel(result) }), 'browse', [{
              name: '<i class="fa fa-home"></i>',
              url: '#/',
            }, {
              name: 'Browse packages',
              url: '#/browse',
            }, {
              name: `${packageName} package details`,
              url: `#/browse/${packageName}`,
              active: true,
            }]);
        })
    },
});

export default AppRouter;
