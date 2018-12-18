import 'fork-awesome/css/fork-awesome.css';

import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { Link, NavLink } from 'react-router-dom';
import { withRouter } from 'react-router';



class Navbar extends React.Component {

    constructor(props) {
        super(props);
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
                                <NavLink key={ key } exact={ item.exact } activeClassName="is-active" className="navbar-item" to={ item.href } >{ item.title }</NavLink>
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


console.log(PropTypes);
Navbar.propTypes = {
    navbarBurgerIsActive: PropTypes.bool.isRequired,
    menuBurgerToggle: PropTypes.func.isRequired,
    navMenu: PropTypes.array.isRequired,
    username: PropTypes.string.isRequired,
};


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

    };
};


export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Navbar));
