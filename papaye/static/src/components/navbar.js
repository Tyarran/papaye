import 'fork-awesome/css/fork-awesome.css';

import PropTypes from 'prop-types';
import React from 'react';
import _ from 'lodash';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { withRouter } from 'react-router';



class Navbar extends React.Component {

    constructor(props) {
        super(props);
    }

    isActiveClass(itemId) {
        const item = _.find(this.props.navMenu, {'id': itemId});
        return (item.active) ? 'is-active': ''
    }

    componentDidMount() {
        this.props.history.listen((location) => {
            this.props.onLocationChange(location);
        });
    }

    render() {
        return (
            <nav className="navbar is-primary" role="navigation" aria-label="main navigation">
                <div className="navbar-brand">
                    <Link
                        className="navbar-item"
                        to="/"
                    >
                        Papaye
                    </Link>
                </div>
                <div 
                    className={`navbar-burger burger ${(this.props.navbarBurgerIsActive) ? 'is-active' : ''}`}
                    data-target="navbar-menu"
                    onClick={(event) => {this.props.menuBurgerToggle(event);}}
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                    
                <div
                    className={`navbar-menu ${(this.props.navbarBurgerIsActive) ? 'is-active' : ''}`}
                    id="navbar-menu"
                >
                    <div className="navbar-start">
                        {this.props.navMenu.map((item, key) => {
                            return (
                                <Link key={key} className={`navbar-item ${this.isActiveClass(item.id)}`} to={item.href} >
                                    {item.title}
                                </Link>
                            );
                        })}
                        <div className="navbar-item">
                            <div className="field">
                                <span className="control has-icons-left">
                                    <span className="icon is-small is-left">
                                        <i className="fa fa-search"></i>
                                    </span>
                                    <input className="input" type="text" placeholder="Search" />
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className="navbar-end">
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <i className="fa fa-user" aria-hidden="true"></i>&nbsp;{this.props.username}
                            </a>
                            <div className="navbar-dropdown">
                                <a className="navbar-item" href="/logout">Logout</a>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
        );
    }
}


const mapStateToProps = (state) => {
    return {
        navMenu: state.get('navMenu'),
        navbarBurgerIsActive: state.get('navbarBurgerIsActive'),
        username: state.get('username'),
    };
};


const mapDispatchToProps = (dispatch) => {
    return {
        menuBurgerToggle(event) {
            event.preventDefault();
            const value = !(this.navbarBurgerIsActive);

            dispatch({type: 'TOGGLE_MENU_BURGER_VISIBILITY', navbarBurgerIsActive: value});
        },

        onLocationChange(location) {
            console.log(location);
            dispatch({type: 'LOCATION_CHANGE', location});
        }
    };
};


export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Navbar));
