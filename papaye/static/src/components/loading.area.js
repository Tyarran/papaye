import React from 'react';
import Spinner from 'react-spinkit';


class LoadingArea extends React.Component {

    render() {
        return (
            <div className='has-text-centered'>
                <Spinner name='three-bounce' className="has-text-centered" />
            </div>
        );
    }
}


export default LoadingArea;
