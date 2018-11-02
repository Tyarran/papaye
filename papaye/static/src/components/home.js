import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import Highlight from './highlight';


class Home extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="section">
                <div className="content container">
                    <h1>Papaye index repository</h1>

                    <h2>How to use this repository</h2>
                    <h3>In one command line</h3>
                    <p>You can use with repository temporarily on pass PIP command argument </p>
                    <Highlight language="bash">pip install your_package -i {this.props.simpleUrl}</Highlight>

                    <h3>Per project configuration</h3>
                    <p>If you want using this repository for only one specific project, you can add this line into the requirements.txt file:</p>
                    <Highlight language="dos">-i {this.props.simpleUrl} .</Highlight>


                    <h3>Permanent configuration</h3>
                    <p>Edit the ~/.pip/pip.conf file like:</p>

                    <Highlight language="ini">{`[install]

    [search]
    index = ${this.props.simpleUrl}`}</Highlight>

                    <h2>Uploading files</h2>

                    Edit your ~/.pypirc file like:
                    <Highlight language="ini" element="code">{`[distutils]
    index-servers =
    papaye

    [papaye]
    username: your_papaye_username
    password: your_papaye_password
    repository: ${this.props.simpleUrl}`}</Highlight>
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return ({
        simpleUrl: state.get('simpleUrl'),
    });
};


Home.propTypes = {
    simpleUrl: PropTypes.string.isRequired
};

export default connect(mapStateToProps)(Home);
