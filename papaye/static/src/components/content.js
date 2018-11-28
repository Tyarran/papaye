import React from 'react';
import { Link } from 'react-router-dom';

import hljs from 'highlightjs';
import _ from 'lodash';


class Content extends React.Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        const blocks = document.getElementsByTagName('pre');

        _.forEach(blocks, (block) => {
            hljs.highlightBlock(block);
        });
    }

    render() {
        return(
            <div className="section">
                <div className="container">
                    <nav className="breadcrumb" aria-label="breadcrumbs">
                    <ul>
                    {
                        this.props.breadcrumb.map((item, key) => {
                            if (key == this.props.breadcrumb.length - 1) {
                                return <li key={key} className="is-active" data-key={key}><a aria-current="page"><span className="icon is-small"><i className={item.icon} aria-hidden="true"></i></span>{item.name}</a></li>
                            }
                            return <li key={key}><Link to={item.href}><span className="icon is-small"><i className={item.icon} aria-hidden="true"></i></span>{item.name}</Link></li>
                        }) 
                    }
                    </ul>
                    </nav>
                </div>
            
                <div className="content container">
                    {this.props.children}
                </div>
            </div>
        );
    }
}
export default Content;
