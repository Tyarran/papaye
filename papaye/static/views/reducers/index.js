'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.reducer = undefined;

var _redux = require('redux');

var _app = require('./app');

var _app2 = _interopRequireDefault(_app);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var reducer = exports.reducer = (0, _redux.combineReducers)({ app: _app2.default });
var store = (0, _redux.createStore)(reducer, {});
exports.default = store;