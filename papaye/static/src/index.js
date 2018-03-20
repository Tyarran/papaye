import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';
import hljs from 'highlightjs';
import 'highlightjs/styles/monokai.css';
import 'bootstrap/dist/css/bootstrap.css';
import _ from 'lodash';


class AppComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: '',
            text: '',
        };
    }

    formSubmit(event) {
        event.preventDefault();

        const newState = Object.assign({}, this.state, {name: this.state.text});
        this.setState(newState);
    }

    handleOnChange(event) { const newState = Object.assign({}, this.state, {text: event.target.value});
        this.setState(newState);
    }

    render() {
        return (
            <div>
                <h1>Hello {this.state.name} !</h1>
                <form action="" className="form-inline">
                    <input
                        type="text"
                        onChange={(event) => this.handleOnChange(event)}
                        placeholder="Enter your name here"
                    />
                    <input
                        type="submit"
                        onClick={(event) => this.formSubmit(event)}
                        value='Click !'
                        className="btn btn-primary"
                    />
                </form>
                <pre className="code">
                    {`
class Test(object):
                        
                        def __call__(self):
                            print Hello `}{this.state.name}{` !

                    test = Test()
                    test()

                      `} </pre>
                <p>{this.state.name}</p>
            </div>
        );
    }

    componentDidMount() {
        const blocks = document.querySelectorAll('.code');
        _.each(blocks, (block) =>{
            hljs.highlightBlock(block);
        });
    }
}

AppComponent.propTypes = {
    name: PropTypes.string,
};


ReactDOM.render(<AppComponent name="Romain" />, document.getElementById('root'));
