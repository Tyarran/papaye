import PropTypes from 'prop-types';
import React from 'react';
import Spinner from 'react-spinkit';

import { connect } from 'react-redux';

//import hljs from 'highlightjs';

import Content from './content';


class PackageDetailsLoad extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <section className="section">
                <div className="container">
                <Spinner name='double-bounce' />
                </div>
            </section>
        );
    }
}


class PackageDetailContent extends React.Component {

    constructor(props) {
        super(props);
    }

    breadcrumb() {
        return [
            {
                name: 'Home',
                href: '/',
                icon: 'fa fa-home',
            },
            {
                name: 'Discover',
                href: '/browse',
                icon: 'fa fa-list',
            },
            {
                name: this.props.package.name,
                href: '#',
                icon: 'fa fa-puzzle-piece',
            },
        ];

    }

    render() {
        return (
            <div>
                <section className="hero is-primary">
                    <div className="hero-body">
                        <div className="container">
                        <h1 className="title">
                            {this.props.package.name}
                        </h1>
                        <h2 className="subtitle">
                            {this.props.package.metadata.summary}
                        </h2>
                        </div>
                    </div>
                </section>
                <Content breadcrumb={this.breadcrumb()}>
                    <section className="section">
                        <div className="columns">
                            <div className="column">
                                <div className="content" dangerouslySetInnerHTML={{__html: this.props.package.metadata.description.content}} />
                            </div>
                            <div className="column is-one-quarter">
                                <aside className="menu">
                                <p className="menu-label">
                                    General
                                </p>
                                <ul className="menu-list">
                                    <li><a>Dashboard</a></li>
                                    <li><a>Customers</a></li>
                                </ul>
                                <p className="menu-label">
                                    Administration
                                </p>
                                <ul className="menu-list">
                                    <li><a>Team Settings</a></li>
                                    <li>
                                    <a className="is-active">Manage Your Team</a>
                                    <ul>
                                        <li><a>Members</a></li>
                                        <li><a>Plugins</a></li>
                                        <li><a>Add a member</a></li>
                                    </ul>
                                    </li>
                                    <li><a>Invitations</a></li>
                                    <li><a>Cloud Storage Environment Settings</a></li>
                                    <li><a>Authentication</a></li>
                                </ul>
                                <p className="menu-label">
                                    Transactions
                                </p>
                                <ul className="menu-list">
                                    <li><a>Payments</a></li>
                                    <li><a>Transfers</a></li>
                                    <li><a>Balance</a></li>
                                </ul>
                                </aside>
                                    <div className="box">test</div>
                                </div>
                        </div>
                    </section>
                </Content>
            </div>
        );
    }
}


class PackageDetails extends React.Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.fetchdata();
        fetch(`${this.props.compatAPIUrl}package/${this.props.match.params.appname}/json`).then((response) => {
            return response.json();
        }).then((json) => {
            this.props.getResult(json);
        });
    }

    render() {
        if (this.props.package) {
            return (
                <PackageDetailContent package={this.props.package} />
            );
        } else {
            return (
                <PackageDetailsLoad />
            );
        }
    }
}


PackageDetails.propTypes = {
    package: PropTypes.object.isRequired,
};


const mapDispatchToProps = (dispatch) => {
    return {
        fetchdata() {
            dispatch({type: 'DETAIL_DATA_FETCH'});
        },
        getResult(response) {
            dispatch({type: 'DETAIL_DATA_READ', package: response.result });
        },
    };
};


const mapStateToProps = (state) => {
    return {
        package: state.get('detail').package || null,
        compatAPIUrl: state.get('compatAPIUrl'),
    };
};


export default connect(mapStateToProps, mapDispatchToProps)(PackageDetails);
