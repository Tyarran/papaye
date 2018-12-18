import 'bulma/css/bulma.css';
import React from 'react';
import PropTypes from 'prop-types';
import { Switch, Route } from 'react-router-dom';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';

import Home from './components/home';
import Navbar from './components/navbar';
import PackageList from './components/package.list';
import PackageDetails from './components/package.detail';


const COMPONENTS = {
    home: Home,
    browse: PackageList,
    detail: PackageDetails,
};


class Main extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <Navbar/>
                <Switch>
                    {this.props.routes.map((item, key) => {
                        return (
                            <Route
                                key={ key }
                                name={item.name}
                                exact={item.exact}
                                path={item.pattern}
                                component={COMPONENTS[item.name]}
                            />);
                    })}
                </Switch>
            </div>
        );
    }
}


Main.propTypes = {
    routes: PropTypes.array.isRequired
};


const mapStateToProps = (state) => {
    return {
        routes: state.get('routes', []),
    };
};


export default withRouter(connect(mapStateToProps, null)(Main));
