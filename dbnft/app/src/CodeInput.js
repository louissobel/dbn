import React from 'react';

import Navbar from 'react-bootstrap/Navbar';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

class CodeInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      code: ""
    };
  }

  onCodeChange(e) {
    this.setState({
      code:  e.target.value,
    })
  }

  onRun(e) {
    this.props.onRun(this.state.code)
  }

  render() {
    return (
      <div className="code-input-holder">
        <Row>
          <Col>
            <textarea
              className="code-input"
              cols="50"
              disabled={this.props.disabled}
              value={this.state.code}
              onChange={this.onCodeChange.bind(this)}
            />
          </Col>
        </Row>
        <Row>
          <Col>
            <Button 
              variant="primary"
              disabled={this.props.disabled}
              onClick={this.onRun.bind(this)}
            >
              Run
            </Button>
          </Col>
        </Row>
      </div>
    )
  }
}

export default CodeInput;
