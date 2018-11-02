'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _propTypes = require('prop-types');

var _propTypes2 = _interopRequireDefault(_propTypes);

var _react = require('react');

var _react2 = _interopRequireDefault(_react);

var _highlight = require('./highlight');

var _highlight2 = _interopRequireDefault(_highlight);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Home = function (_React$Component) {
    _inherits(Home, _React$Component);

    function Home(props) {
        _classCallCheck(this, Home);

        return _possibleConstructorReturn(this, (Home.__proto__ || Object.getPrototypeOf(Home)).call(this, props));
    }

    _createClass(Home, [{
        key: 'render',
        value: function render() {
            return _react2.default.createElement(
                'div',
                { className: 'content container' },
                _react2.default.createElement(
                    'h1',
                    null,
                    'Papaye index repository'
                ),
                _react2.default.createElement(
                    'h2',
                    null,
                    'How to use this repository'
                ),
                _react2.default.createElement(
                    'h3',
                    null,
                    'In one command line'
                ),
                _react2.default.createElement(
                    'p',
                    null,
                    'You can use with repository temporarily on pass PIP command argument '
                ),
                _react2.default.createElement(
                    _highlight2.default,
                    { className: 'bash' },
                    'pip install your_package -i ',
                    this.props.simpleUrl
                ),
                _react2.default.createElement(
                    'h3',
                    null,
                    'Per project configuration'
                ),
                _react2.default.createElement(
                    'p',
                    null,
                    'If you want using this repository for only one specific project, you can add this line into the requirements.txt file:'
                ),
                _react2.default.createElement(
                    _highlight2.default,
                    { className: 'dos' },
                    '-i ',
                    this.props.simpleUrl,
                    ' .'
                ),
                _react2.default.createElement(
                    'h3',
                    null,
                    'Permanent configuration'
                ),
                _react2.default.createElement(
                    'p',
                    null,
                    'Edit the ~/.pip/pip.conf file like:'
                ),
                _react2.default.createElement(
                    _highlight2.default,
                    { className: 'ini' },
                    '[install]\n\n[search]\nindex = ' + this.props.simpleUrl
                ),
                _react2.default.createElement(
                    'h2',
                    null,
                    'Uploading files'
                ),
                'Edit your ~/.pypirc file like:',
                _react2.default.createElement(
                    _highlight2.default,
                    { className: 'ini', element: 'code' },
                    '[distutils]\nindex-servers =\npapaye\n\n[papaye]\nusername: your_papaye_username\npassword: your_papaye_password\nrepository: ' + this.props.simpleUrl
                )
            );
        }
    }]);

    return Home;
}(_react2.default.Component);

Home.propTypes = {
    simpleUrl: _propTypes2.default.string.isRequired
};

exports.default = Home;