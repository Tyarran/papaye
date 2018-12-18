import React from 'react';


class Safe extends React.Component {
    
    render() {
        return (
            <div className={ this.props.className } dangerouslySetInnerHTML={{__html: this.props.htmlText }} /> 
        );
    }
}

export default Safe;
