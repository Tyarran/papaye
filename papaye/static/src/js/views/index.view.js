import Marionette from 'backbone.marionette';
import _ from 'underscore';
import hljs from 'highlightjs';

import Handlebars from 'handlebars';

import indexTemplate from '../../templates/index.template.html!text';

import 'highlightjs/styles/monokai.css!';
import 'highlightjs/styles/monokai_sublime.css!';


const IndexView = Marionette.LayoutView.extend({
    template: Handlebars.compile(indexTemplate),

    ui: {
        codeBlocks: 'pre',
    },

    templateHelpers: {
        simple_url: window.APP_CONTEXT.urls.simple,
    },

    onShow() {
        _.each(this.ui.codeBlocks, (block) => {
            hljs.highlightBlock(block);
        });
    }
});

export default IndexView;
