import 'bulma/css/bulma.css';
import React from 'react';
import { Route } from 'react-router-dom';

import Home from './components/home';
import Navbar from './components/navbar';
import BrowseList from './components/browseList';


class Main extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <Navbar/>
                <div className="container">
                    <Route exact path="/" component={Home} />
                    <Route path="/browse/detail/:appname" component={Home} />
                    <Route path="/browse" component={BrowseList} />
                </div>
            </div>
        );
    }
}


export default Main;
