import React from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

import hljs from 'highlightjs';

class Content extends React.Component {

    static propTypes = {
        children: PropTypes.any,
        breadcrumb: PropTypes.array.isRequired,
    }

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        const blocks = Array.from(document.getElementsByTagName('pre'));

        blocks.forEach(block => hljs.highlightBlock(block));
    }

    componentDidUpdate() {
        this.componentDidMount();
    }

    renderBreadcrumb() {
        let breadcrumbItems = [];
        if (this.props.breadcrumb !== null) {
            breadcrumbItems = this.props.breadcrumb.map((item, key) => {
                if (key == this.props.breadcrumb.length - 1) {
                    return <li key={key} className="is-active" data-key={key}><a aria-current="page"><span className="icon is-small"><i className={item.icon} aria-hidden="true"></i></span>{item.name}</a></li>;
                }
                return <li key={key}><Link to={item.href}><span className="icon is-small"><i className={item.icon} aria-hidden="true"></i></span>{item.name}</Link></li>;
            });
        }
        return (
            <nav className="breadcrumb" aria-label="breadcrumbs">
                <ul>
                    { breadcrumbItems }
                </ul>
            </nav>
        );
    }

    render() {
        return(
            <div>
                <div className="content container">
                    <div className="section">
                        { this.renderBreadcrumb() }
                        {this.props.children}
                    </div>
                </div>
            </div>
        );
    }
}


export default Content;
