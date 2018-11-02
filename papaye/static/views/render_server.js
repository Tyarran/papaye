'use strict';

var _server = require('react-dom/server');

var _yargs = require('yargs');

var _yargs2 = _interopRequireDefault(_yargs);

var _bodyParser = require('body-parser');

var _bodyParser2 = _interopRequireDefault(_bodyParser);

var _Console = require('Console');

var _Console2 = _interopRequireDefault(_Console);

var _express = require('express');

var _express2 = _interopRequireDefault(_express);

var _http = require('http');

var _http2 = _interopRequireDefault(_http);

var _react = require('react');

var _react2 = _interopRequireDefault(_react);

var _server2 = require('../dist/server.bundle');

var _server3 = _interopRequireDefault(_server2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

_Console2.default.log(_server3.default);

var argv = _yargs2.default.option('p', {
    alias: 'port',
    description: 'Specify the server\'s port',
    default: 9009
}).option('a', {
    alias: 'address',
    description: 'Specify the server\'s address',
    default: '127.0.0.1'
}).help('h').alias('h', 'help').strict().argv;

var ADDRESS = argv.address;
var PORT = argv.port;
var app = (0, _express2.default)();
var server = _http2.default.Server(app);

app.use(_bodyParser2.default.json());

app.post('/render', function (req, res) {
    res.write((0, _server.renderToString)(_react2.default.createElement(_server3.default, null)));
    _Console2.default.log((0, _server.renderToString)(_react2.default.createElement(_server3.default, null)));
    res.end();
});

server.listen(PORT, ADDRESS, function () {
    _Console2.default.success('React render server listening at http://' + ADDRESS + ':' + PORT);
});