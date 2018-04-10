import 'bulma/css/bulma.css';
import 'open-iconic/font/css/open-iconic.css';
import Navbar from './components/navbar';
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Router, Link, Route, IndexRoute, BrowserHistory } from 'react-router-dom';
import createBrowserHistory from 'history/createBrowserHistory'

const customHistory = createBrowserHistory();
console.log(customHistory);


class Dashboard extends React.Component {
    render() {
        return (
            <div>Dashboard component !!!</div>
        );
    }
}

class Dashboard2 extends React.Component {
    render() {
        return (
            <div>Dashboard2 component !!!!!</div>
        );
    }
}

class Dashboard3 extends React.Component {
    render() {
        return (
            <div>Dashboard3 component !!!</div>
        );
    }
}


class AppComponent extends React.Component {
    render() {
        return (
            <div>
                <Navbar />
                <div className="container">
                    <Link to="/dashboard">dashboard</Link>
                    <Link to="/dashboard2">dashboard2</Link>
                </div>
                <Route path ="/" component={Dashboard} />
                <Route path="/browse" component={Dashboard2} />
                <Route path="/api" component={Dashboard3} />
            </div>
        );
    }
}


ReactDOM.render(
    <BrowserRouter>
        <AppComponent name="Romain" />
    </BrowserRouter>
    , document.getElementById('root')
);
