import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';


class PackageListItem extends React.Component {

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


PackageListItem.propTypes = {
    name: PropTypes.string.isRequired, 
    summary: PropTypes.string,
};

export default PackageListItem;
