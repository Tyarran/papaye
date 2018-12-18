import React from 'react';
import PropTypes from 'prop-types';



class PackageHero extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <section className="hero is-primary">
                <div className="hero-body">
                    <div className="container">
                        <h1 className="title">
                            {this.props.name}
                        </h1>
                        <h2 className="subtitle">
                            {this.props.summary}
                        </h2>
                    </div>
                </div>
            </section>
        );
    }
}


PackageHero.propTypes = {
    name: PropTypes.string.isRequired,
    summary: PropTypes.string.isRequired,
};


export default PackageHero;
