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
        var blocks = document.getElementsByTagName('pre');

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
            <pre className={this.props.language}>{this.props.children}</pre>
        );
    }

}

Highlight.propTypes = {
    language: PropTypes.string,
    // children: PropTypes.bool,
};

export default Highlight;
