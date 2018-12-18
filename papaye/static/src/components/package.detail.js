import PropTypes from 'prop-types';
import React from 'react';

import { connect } from 'react-redux';
import { withRouter } from 'react-router';

import Content from './content';
import PackageHero from './package.hero';
import LoadingArea from './loading.area';
import PackageMetadata from './package.metadata';
import Safe from './safe';



class PackageDetailContent extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <section className="section">
                <div className="columns">
                    <div className="column">
                        <Safe className="content" htmlText={ this.props.package.metadata.description.content } />
                    </div>
                    <div className="column is-one-quarter">
                        <PackageMetadata />
                    </div>
                </div>
            </section>
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
                name: (this.props.package !== null) ? this.props.package.name : this.props.match.params.appname,
                href: '#',
                icon: 'fa fa-puzzle-piece',
            },
        ];

    }


    getContent() {
        return (this.props.package !== null) ? <PackageDetailContent package={this.props.package} /> : <LoadingArea />;
    }

    getHero() {
        if (this.props.package) {
            return <PackageHero name={ this.props.package.name } summary={ this.props.package.metadata.summary } />;
        } else {
            return <PackageHero name={ this.props.match.params.appname } summary={ '' } />;
        }
    }

    render() {
        return (
            <div>
                { this.getHero() }
                <Content breadcrumb={this.breadcrumb()}>
                    { this.getContent() }
                </Content>
            </div>
        );
    }
}


PackageDetails.propTypes = {
    package: PropTypes.object,
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


export default withRouter(connect(mapStateToProps, mapDispatchToProps)(PackageDetails));
