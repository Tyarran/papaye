'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _actions = require('../actions');

var _actions2 = _interopRequireDefault(_actions);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var window = {};

var initialState = { bidule: ';askdjfs;lfjkd',
    simpleUrl: 'http://localhost:6543/simple',
    username: 'Romain',
    navbarBurgerIsActive: false,
    navMenu: [{ id: 'home',
        title: 'Home',
        href: '/',
        active: false,
        exact: false }, { id: 'browse', title: 'Browse', href: '/browse', active: false }, { id: 'api', title: 'API', href: '/api', active: false }] };

var appReducer = function appReducer(state, action) {
    var newState = Object.assign({}, state);
    switch (action.type) {
        case _actions2.default.TOGGLE_MENU_BURGER_VISIBILITY.type:
            newState.navbarBurgerIsActive = action.navbarBurgerIsActive;
            return newState;
        default:
            return initialState;
    }
};

exports.default = appReducer;