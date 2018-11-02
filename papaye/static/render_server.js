import { renderToString } from "react-dom/server";
import Argv from 'yargs';
import bodyParser from 'body-parser';
import Console from 'Console';
import express from 'express';
import http from 'http';
import React from 'react';
import { StaticRouter, BrowserRouter } from 'react-router-dom';
import { Map } from 'immutable';

import { Provider } from 'react-redux';
import { createStore } from 'redux';

import Main from './src/index';
import appReducer from './src/reducers';


var argv = Argv.option('p', {
    alias: 'port',
    description: 'Specify the server\'s port',
    default: 9009
}).option('a', {
    alias: 'address',
    description: 'Specify the server\'s address',
    default: '127.0.0.1'
}).help('h').alias('h', 'help').strict().argv;

const ADDRESS = argv.address;
const PORT = argv.port;
const app = express();
const server = http.Server(app);

app.use(bodyParser.json());


app.post('/render', (req, res) => {
    const initialState = Map(req.body.state);
    const store = createStore(appReducer, initialState);
    const context = {};

    res.write(renderToString(
        <StaticRouter location={ {pathname: req.body.path} } context={context}>
            <Provider store={store}>
                <Main/>
            </Provider>
        </StaticRouter>
    ));
    Console.log(renderToString(
        <StaticRouter location={ {pathname: req.body.path} } context={context}>
            <Provider store={store}>
                <Main/>
            </Provider>
        </StaticRouter>
    ));
    res.end();
});

server.listen(PORT, ADDRESS, function() {
    Console.success('React render server listening at http://' + ADDRESS + ':' + PORT);
});
