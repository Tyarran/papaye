import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import { BrowserRouter } from 'react-router-dom';
import { Map } from 'immutable';

import Main from './index';
import appReducer from './reducers';

const store = createStore(
    appReducer,
    Map(window.INITIAL_STATE),
    window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);


ReactDOM.hydrate(
    <BrowserRouter>
        <Provider store={store}>
            <Main/>
        </Provider>
    </BrowserRouter>,
    document.getElementById('root'));

export default Main;
