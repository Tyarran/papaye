import 'bulma/css/bulma.css';
import React from 'react';
import { Switch, Route } from 'react-router-dom';

import Home from './components/home';
import Navbar from './components/navbar';
import BrowseList from './components/browseList';
import PackageDetails from './components/package.detail';


class Main extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <Navbar/>
                <Switch>
                        <Route exact path="/" component={Home} breadcrumb='/' />
                        <Route path="/browse/detail/:appname" component={PackageDetails} />
                        <Route exact path="/browse" component={BrowseList} />
                </Switch>
            </div>
        );
    }
}


export default Main;
