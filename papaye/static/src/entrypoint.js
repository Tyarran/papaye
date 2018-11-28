import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import { BrowserRouter } from 'react-router-dom';
import { Map } from 'immutable';

import Main from './index.js';
import appReducer from './reducers';

const store = createStore(
    appReducer,
    Map(window.INITIAL_STATE),
    window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);


function onUpdate() {
    console.log("onChange");
};


ReactDOM.hydrate(
    <BrowserRouter onChange={onUpdate.bind(this)}>
        <Provider store={store}>
            <Main/>
        </Provider>
    </BrowserRouter>,
    document.getElementById('root'));

export default Main;
