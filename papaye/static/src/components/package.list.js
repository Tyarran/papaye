import React from 'react';
import fetch from 'cross-fetch';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import Content from './content';
import PackageListItem from './package.list.item';


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


class PackageList extends React.Component {

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
                            <PackageListItem key={key} name={item.name} summary={item.summary} />
                        );
                    })}
                </div>
            </Content>
        );
    }
}

PackageList.propTypes = {
    fetchdata: PropTypes.func.isRequired,
    getResult: PropTypes.func.isRequired,
    filterList: PropTypes.func.isRequired,
    compatAPIUrl: PropTypes.string.isRequired,
    filteredPackageList: PropTypes.array.isRequired,
};

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


export default connect(mapStateToProps, mapDispatchToProps)(PackageList);
