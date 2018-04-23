import 'open-iconic/font/css/open-iconic.css';
import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { NavLink, withRouter } from 'react-router-dom';


class NavbarItem extends React.Component {
    constructor(props) {
        super(props);
    }

    onClick(event) {
        event.preventDefault();
        this.props.notifier(this.props.id);
    }

    render() {
        return (
            <NavLink
                className="navbar-item"
                to={this.props.href}
                exact
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
    }

    render() {
        return (
            <nav className="navbar is-primary" role="navigation" aria-label="main navigation">
                <div className="navbar-brand">
                    <NavLink
                        className="navbar-item"
                        to="/"
                        exact
                    >
                        Papaye
                    </NavLink>
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
                            return <NavbarItem key={key} id={key} title={item.title} href={item.href} />;
                        })}
                    </div>
                    <div className="navbar-end">
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="oi" data-glyph="person"></span>&nbsp;{this.props.username}
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
    console.log(state);
    return {
        navMenu: state.testReducer.navMenu,
        navbarBurgerIsActive: state.testReducer.navbarBurgerIsActive,
    };
};


const mapDispatchToProps = (dispatch) => {
    return {
        menuBurgerToggle(event) {
            event.preventDefault();
            const value = !(this.navbarBurgerIsActive);

            dispatch({type: 'TOGGLE_MENU_BURGER_VISIBILITY', navbarBurgerIsActive: value});
        }
    };
};



export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Navbar));
