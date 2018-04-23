import 'bulma/css/bulma.css';
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Route, Switch, withRouter } from 'react-router-dom';
import { Provider, connect } from 'react-redux';
import PropTypes from 'prop-types';

import Navbar from './components/navbar';
import Home from './components/home';
import store from './reducers';


class Dashboard2 extends React.Component {
    render() {
        return (
            <div>
                Dashboard2 component !!!!!
            </div>
        );
    }
}

class Dashboard3 extends React.Component {
    render() {
        return (
            <div>
                Dashboard3 component !!!
            </div>
        );
    }
}


class AppComponent extends React.Component {

    constructor(props) {
        super(props);
        //this.state = window.state;
    }

    render() {
        return (
            <div >
                <Navbar username={this.props.username}k/>
                <Switch>
                    <Route exact path="/" render={() => <Home simpleUrl={this.props.simpleUrl} /> } />
                    <Route path="/browse" component={Dashboard2} />
                    <Route path="/api" component={Dashboard3} />
                </Switch>
            </div>
        );
    }
}

AppComponent.propTypes = {
    username: PropTypes.string.isRequired,
    simpleUrl: PropTypes.string.isRequired,
};


const mapStateToProps = (state) => {
    return {
        username: state.testReducer.username,
        simpleUrl: state.testReducer.simpleUrl
    };
};


const mapDispatchToProps = () => {
    return { };
};


const App = withRouter(connect(mapStateToProps, mapDispatchToProps)(AppComponent));


ReactDOM.render(
    <BrowserRouter>
        <Provider store={store}>
            <App />
        </Provider>
    </BrowserRouter>
    , document.getElementById('root')
);
