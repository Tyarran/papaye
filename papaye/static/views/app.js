'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = require('react');

var _react2 = _interopRequireDefault(_react);

var _reactDom = require('react-dom');

var _reactDom2 = _interopRequireDefault(_reactDom);

var _reactRedux = require('react-redux');

var _propTypes = require('prop-types');

var _propTypes2 = _interopRequireDefault(_propTypes);

var _navbar = require('./components/navbar');

var _navbar2 = _interopRequireDefault(_navbar);

var _home = require('./components/home');

var _home2 = _interopRequireDefault(_home);

var _reducers = require('./reducers');

var _reducers2 = _interopRequireDefault(_reducers);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } //import 'bulma/css/bulma.css';

//import { BrowserRouter, Route, Switch, withRouter } from 'react-router-dom';


var Dashboard2 = function (_React$Component) {
    _inherits(Dashboard2, _React$Component);

    function Dashboard2() {
        _classCallCheck(this, Dashboard2);

        return _possibleConstructorReturn(this, (Dashboard2.__proto__ || Object.getPrototypeOf(Dashboard2)).apply(this, arguments));
    }

    _createClass(Dashboard2, [{
        key: 'render',
        value: function render() {
            return _react2.default.createElement(
                'div',
                null,
                'Dashboard2 component !!!!!'
            );
        }
    }]);

    return Dashboard2;
}(_react2.default.Component);

var Dashboard3 = function (_React$Component2) {
    _inherits(Dashboard3, _React$Component2);

    function Dashboard3() {
        _classCallCheck(this, Dashboard3);

        return _possibleConstructorReturn(this, (Dashboard3.__proto__ || Object.getPrototypeOf(Dashboard3)).apply(this, arguments));
    }

    _createClass(Dashboard3, [{
        key: 'render',
        value: function render() {
            return _react2.default.createElement(
                'div',
                null,
                'Dashboard3 component !!!'
            );
        }
    }]);

    return Dashboard3;
}(_react2.default.Component);

var AppComponent = function (_React$Component3) {
    _inherits(AppComponent, _React$Component3);

    function AppComponent(props) {
        _classCallCheck(this, AppComponent);

        return _possibleConstructorReturn(this, (AppComponent.__proto__ || Object.getPrototypeOf(AppComponent)).call(this, props));
    }

    _createClass(AppComponent, [{
        key: 'render',
        value: function render() {
            return _react2.default.createElement(
                _reactRedux.Provider,
                { store: _reducers2.default },
                _react2.default.createElement(
                    'div',
                    null,
                    _react2.default.createElement(_navbar2.default, { username: this.props.username, k: true })
                )
            );
        }
    }]);

    return AppComponent;
}(_react2.default.Component);

var mapStateToProps = function mapStateToProps(state) {
    return {
        username: state.app.username,
        simpleUrl: state.app.simpleUrl
    };
};

AppComponent.propTypes = {
    username: _propTypes2.default.string.isRequired,
    simpleUrl: _propTypes2.default.string.isRequired
};

//const App = withRouter(connect(mapStateToProps, null)(AppComponent));

exports.default = (0, _reactRedux.connect)(mapStateToProps, null)(AppComponent);