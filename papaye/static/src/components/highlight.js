import 'highlightjs/styles/tomorrow-night.css';
import PropTypes from 'prop-types';
import React from 'react';
import _ from 'lodash';
import hljs from 'highlightjs';


class Highlight extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        const blocks = document.getElementsByTagName('pre');

        _.forEach(blocks, (block) => {
            hljs.highlightBlock(block);
        });

    }
    
    componentDidUpdate() {
        const blocks = document.getElementsByTagName('pre');

        _.forEach(blocks, (block) => {
            hljs.highlightBlock(block);
        });

    }

    render() {
        return(
            <pre className={this.props.className}>{this.props.children}</pre>
        );
    }

}

Highlight.propTypes = {
    className: PropTypes.string,
    children: PropTypes.array,
};

export default Highlight;
