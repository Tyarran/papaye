'use strict';

var _reactRouterDom = require('react-router-dom');

var _reactRedux = require('react-redux');

var _redux = require('redux');

var _app = require('./app');

var _app2 = _interopRequireDefault(_app);

var _app3 = require('./reducers/app');

var _app4 = _interopRequireDefault(_app3);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var App = withRouter(_app2.default);
var store = (0, _redux.createStore)(reducer);

hydrate(React.createElement(
    _reactRedux.Provider,
    { store: store },
    React.createElement(
        _reactRouterDom.BrowserRouter,
        null,
        React.createElement(App, null)
    )
), document.getElementById('root'));