import Marionette from 'backbone.marionette';
import Backbone from 'backbone';

import AppView from './views/app.view';
import AppRouter from './routers';


const PapayeApplication = Marionette.Application.extend({

    onBeforeStart() {
        console.log('Initializing application');
        this.router = new AppRouter();
    },

    onStart() {
        console.log('Application is starting');
        const appView = new AppView({
            el: '#container',
            router: this.router,
        });
        appView.render();
        Backbone.history.start();
    }
});


const app = new PapayeApplication();
app.start();
