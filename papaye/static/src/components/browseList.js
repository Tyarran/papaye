import React from 'react';
import fetch from 'cross-fetch';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import Content from './content';


const breadcrumb = [
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
];


class PackageItem extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="column is-half">
                <div className="box">
                    <div className="media-content">
                        <div className="content">
                            <strong>{this.props.name}</strong> <small>{this.props.name}</small>
                            <p>{this.props.summary}</p>
                            <p>
                                <span className="tag is-info is-small">Local</span>
                                <span className="tag is-success is-small">Public</span>
                                <span className="tag is-warning is-small">Cached</span>
                            </p>
                        </div>
                        <Link to={`/browse/detail/${this.props.name}`} >Details</Link>

                    </div>
                </div>
            </div>
        );
    }
}


class BrowseList extends React.Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.fetchdata();
        fetch(`${this.props.compatAPIUrl}package/json`).then((response) => {
            return response.json();
        }).then((json) => {
            this.props.getResult(json);
        });
    }
    

    handleKeyPress(event) {
        const pattern = event.target.value;
        this.props.filterList(pattern);
    }

    render() {
        return (
            <Content breadcrumb={breadcrumb}>
                <div className="field is-grouped">
                    <p className="control is-expanded">
                        <input type="text" placeholder="Filter by name" className="input" onKeyUp={this.handleKeyPress.bind(this)}/>
                    </p>
                    <div className="control">
                        <div className="buttons has-addons">
                            <input type="button" className="button is-primary" value="local" />
                            <input type="button" className="button is-primary" value="public" />
                            <input type="button" className="button is-primary" value="cached" />
                        </div>
                    </div>
                </div>
                <div className="columns is-multiline">
                    {this.props.filteredPackageList.map((item, key) => {
                        return (
                            <PackageItem key={key} name={item.name} summary={item.summary} />
                        );
                    })}
                </div>
            </Content>
        );
    }
}


const mapStateToProps = (state) => {
    return {
        filteredPackageList: state.get('filteredPackageList', []),
        compatAPIUrl: state.get('compatAPIUrl'),
    };
};


const mapDispatchToProps = (dispatch) => {
    return {
        fetchdata() {
            dispatch({type: 'DATA_FETCH'});
        },
        getResult(response) {
            dispatch({type: 'DATA_READ', response: response.result });
        },
        filterList(pattern) {
            dispatch({type: 'DATA_FILTER', pattern});
        }
    };
};


export default connect(mapStateToProps, mapDispatchToProps)(BrowseList);
