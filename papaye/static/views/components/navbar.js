'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _propTypes = require('prop-types');

var _propTypes2 = _interopRequireDefault(_propTypes);

var _react = require('react');

var _react2 = _interopRequireDefault(_react);

var _reactRedux = require('react-redux');

var _reactRouterDom = require('react-router-dom');

var _reducers = require('../reducers');

var _reducers2 = _interopRequireDefault(_reducers);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } //import 'open-iconic/font/css/open-iconic.css';


var NavbarItem = function (_React$Component) {
    _inherits(NavbarItem, _React$Component);

    function NavbarItem(props) {
        _classCallCheck(this, NavbarItem);

        return _possibleConstructorReturn(this, (NavbarItem.__proto__ || Object.getPrototypeOf(NavbarItem)).call(this, props));
    }

    _createClass(NavbarItem, [{
        key: 'onClick',
        value: function onClick() {
            _reducers2.default.dispatch({ type: 'TOGGLE_MENU_BURGER_VISIBILITY' });
        }
    }, {
        key: 'render',
        value: function render() {
            return _react2.default.createElement(
                _reactRouterDom.NavLink,
                {
                    className: 'navbar-item',
                    to: this.props.href,
                    exact: true,
                    activeClassName: 'is-active',
                    onClick: this.onClick.bind(this)
                },
                this.props.title
            );
        }
    }]);

    return NavbarItem;
}(_react2.default.Component);

NavbarItem.propTypes = {
    id: _propTypes2.default.number,
    title: _propTypes2.default.string,
    active: _propTypes2.default.bool,
    href: _propTypes2.default.string
};

var Navbar = function (_React$Component2) {
    _inherits(Navbar, _React$Component2);

    function Navbar(props) {
        _classCallCheck(this, Navbar);

        return _possibleConstructorReturn(this, (Navbar.__proto__ || Object.getPrototypeOf(Navbar)).call(this, props));
    }

    _createClass(Navbar, [{
        key: 'render',
        value: function render() {
            var _this3 = this;

            return _react2.default.createElement(
                'nav',
                { className: 'navbar is-primary', role: 'navigation', 'aria-label': 'main navigation' },
                _react2.default.createElement(
                    'div',
                    { className: 'navbar-brand' },
                    _react2.default.createElement(
                        _reactRouterDom.NavLink,
                        {
                            className: 'navbar-item',
                            to: '/',
                            exact: true
                        },
                        'Papaye'
                    )
                ),
                _react2.default.createElement(
                    'div',
                    {
                        className: 'navbar-burger burger ' + (this.props.navbarBurgerIsActive ? 'is-active' : ''),
                        'data-target': 'navbar-menu',
                        onClick: function onClick(event) {
                            _this3.props.menuBurgerToggle(event);
                        }
                    },
                    _react2.default.createElement('span', null),
                    _react2.default.createElement('span', null),
                    _react2.default.createElement('span', null)
                ),
                _react2.default.createElement(
                    'div',
                    {
                        className: 'navbar-menu ' + (this.props.navbarBurgerIsActive ? 'is-active' : ''),
                        id: 'navbar-menu'
                    },
                    _react2.default.createElement(
                        'div',
                        { className: 'navbar-start' },
                        this.props.navMenu.map(function (item, key) {
                            return _react2.default.createElement(NavbarItem, { key: key, id: key, title: item.title, href: item.href });
                        })
                    ),
                    _react2.default.createElement(
                        'div',
                        { className: 'navbar-end' },
                        _react2.default.createElement(
                            'div',
                            { className: 'navbar-item has-dropdown is-hoverable' },
                            _react2.default.createElement(
                                'a',
                                { className: 'navbar-link' },
                                _react2.default.createElement('span', { className: 'oi', 'data-glyph': 'person' }),
                                '\xA0',
                                this.props.username
                            ),
                            _react2.default.createElement(
                                'div',
                                { className: 'navbar-dropdown' },
                                _react2.default.createElement(
                                    'a',
                                    { className: 'navbar-item', href: '/logout' },
                                    'Logout'
                                )
                            )
                        )
                    )
                )
            );
        }
    }]);

    return Navbar;
}(_react2.default.Component);

var mapStateToProps = function mapStateToProps(state) {
    return {
        navMenu: state.app.navMenu,
        navbarBurgerIsActive: state.app.navbarBurgerIsActive
    };
};

var mapDispatchToProps = function mapDispatchToProps(dispatch) {
    return {
        menuBurgerToggle: function menuBurgerToggle(event) {
            event.preventDefault();
            var value = !this.navbarBurgerIsActive;

            dispatch({ type: 'TOGGLE_MENU_BURGER_VISIBILITY', navbarBurgerIsActive: value });
        }
    };
};

//export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Navbar));
exports.default = (0, _reactRedux.connect)(mapStateToProps, mapDispatchToProps)(Navbar);