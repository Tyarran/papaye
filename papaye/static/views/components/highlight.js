'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _propTypes = require('prop-types');

var _propTypes2 = _interopRequireDefault(_propTypes);

var _react = require('react');

var _react2 = _interopRequireDefault(_react);

var _lodash = require('lodash');

var _lodash2 = _interopRequireDefault(_lodash);

var _highlightjs = require('highlightjs');

var _highlightjs2 = _interopRequireDefault(_highlightjs);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } //import 'highlightjs/styles/tomorrow-night.css';


var Highlight = function (_React$Component) {
    _inherits(Highlight, _React$Component);

    function Highlight(props) {
        _classCallCheck(this, Highlight);

        return _possibleConstructorReturn(this, (Highlight.__proto__ || Object.getPrototypeOf(Highlight)).call(this, props));
    }

    _createClass(Highlight, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var blocks = document.getElementsByTagName('pre');

            _lodash2.default.forEach(blocks, function (block) {
                _highlightjs2.default.highlightBlock(block);
            });
        }
    }, {
        key: 'componentDidUpdate',
        value: function componentDidUpdate() {
            var blocks = document.getElementsByTagName('pre');

            _lodash2.default.forEach(blocks, function (block) {
                _highlightjs2.default.highlightBlock(block);
            });
        }
    }, {
        key: 'render',
        value: function render() {
            return _react2.default.createElement(
                'pre',
                { className: this.props.className },
                this.props.children
            );
        }
    }]);

    return Highlight;
}(_react2.default.Component);

Highlight.propTypes = {
    className: _propTypes2.default.string,
    children: _propTypes2.default.bool
};

exports.default = Highlight;