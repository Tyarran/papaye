import PropTypes from 'prop-types';
import React from 'react';
import _ from 'lodash';
import { NavLink, Route } from 'react-router-dom';


class NavbarItem extends React.Component {
    constructor(props) {
        super(props);
    }

    onClick(event) {
        event.preventDefault();
        this.props.notifier(this.props.id);
    }

    render() {
        const className = `navbar-item ${(this.props.active) ? 'is-active': ''}`;
        return (
            <NavLink
                className="navbar-item"
                to={this.props.href}
                exact={this.props.exact}
                activeClassName="is-active"
            >
                {this.props.title}
            </NavLink>
        );
    }
}

NavbarItem.propTypes = {
    id: PropTypes.number,
    title:  PropTypes.string,
    notifier: PropTypes.func,
    active: PropTypes.bool,
    href: PropTypes.string,
};


class Navbar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            navMenu: [
                {
                    id: 'home',
                    title: 'Home',    
                    href: '',
                    active: false,
                    exact: true,
                },
                {
                    id: 'browse',
                    title: 'Browse',
                    href: '/browse',
                    active: false,
                },
                {
                    id: 'api',
                    title: 'API',
                    href: '/api',
                    active: false,
                }
            ],
            navbarBurgerIsActive: false,
        };
    }

    changeActiveNavItem(key) {
        const newState = Object.assign({}, this.state); 
        
        _.forEach(newState.navMenu, (item) => {
            item.active = false;
        });
        newState.navMenu[key].active = true;

        this.setState(newState);
    }

    toggle(event) {
        event.preventDefault();
        const newState = Object.assign({}, this.state);
        const value = !(this.state.navbarBurgerIsActive);

        newState.navbarBurgerIsActive = value;
        this.setState(newState);
    }


    render() {
        return (
            <nav className="navbar is-primary" role="navigation" aria-label="main navigation">
                <div className="navbar-brand">
                    <a className="navbar-item" href="/">
                        Papaye
                    </a>
                </div>
                <div 
                    className={`navbar-burger burger ${(this.state.navbarBurgerIsActive) ? 'is-active' : ''}`}
                    data-target="navbar-menu"
                    onClick={(event) => {this.toggle(event);}}
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                    
                <div
                    className={`navbar-menu ${(this.state.navbarBurgerIsActive) ? 'is-active' : ''}`}
                    id="navbar-menu"
                >
                    <div className="navbar-start">
                        {this.state.navMenu.map((item, key) => {
                            return <NavbarItem key={key} id={key} title={item.title} href={item.href} exact={item.exact === true ? true: false} active={item.active} notifier={this.changeActiveNavItem.bind(this)} />;
                        })}
                    </div>
                    <div className="navbar-end">
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="oi" data-glyph="person"></span>&nbsp;Admin
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


export default Navbar;
