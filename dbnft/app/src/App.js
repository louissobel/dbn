import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';
import {ethers} from 'ethers';

import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';

import {evmAssemble, evmInterpret} from './evm_tools'
import CodeInput from './CodeInput'
import ImageViewer from './ImageViewer'


const COMPILE_PATH = '/evm_compile'


function App() {
  return (
    <>
      <Navbar bg="dark" variant="dark">
        <Container>
          <Navbar.Brand href="#">DBNFT</Navbar.Brand>
        </Container>
      </Navbar>

      <Container>
        <DBNEditor />
      </Container>
    </>
  );
}

class DBNEditor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rendering: false,
      logLines: [],
      imgURL : "",

    };

  }

  finishLogLine(message) {
    var current = this.state.logLines;
    if (current.length === 0) {
      return;
    }

    var latest = current.pop()
    latest = latest + message
    this.setState({logLines: current.concat([latest])})
  }

  addLogLine(message) {
    this.setState({
      logLines: this.state.logLines.concat([message])
    })
  }

  dbnRender(code) {
    this.setState({
      rendering: true,
      logLines: []
    }, () => {
      this.addLogLine("Compiling... ")
    })
    
    fetch(COMPILE_PATH, {
      method: 'POST',
      body: code

    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Unexpected result: ' + response.status);
      }
      this.finishLogLine("OK!")

      return response.text()
    })
    .then(data => {
      this.addLogLine("Assembling... ")
      console.log(data)
      return evmAssemble(data)
    })
    .then(bytecode => {
      this.finishLogLine("OK!")
      console.log(bytecode)
      this.addLogLine(" → Code Length: " + (bytecode.length - 2)/2);

      this.addLogLine("Interpreting... ")
      return evmInterpret(bytecode)
    })
    .then(result => {
      if (result.exceptionError) {
        throw new Error(result.exceptionError.error)        
      }
      this.finishLogLine("OK!")
      this.addLogLine(" → Gas Used: " + result.gasUsed.toString(10));

      const bitmapData = result.returnValue.slice(64)
      const bitmapBlob = new Blob([bitmapData], {type: 'image/bmp'})

      this.setState({
        imageData: bitmapBlob,
        rendering: false,
      })
    })
    .catch(error => {
      this.finishLogLine(error)
      console.error('', error)
      this.setState({rendering: false})
    });
  }

  onCodeChange(e) {
    this.setState({
      code:  e.target.value,
    })
  }

  render() {
    return (
        <Row className="pt-5">
          <Col>
            <ImageViewer
              imageData={this.state.imageData}
            />

          </Col>
          <Col>
            <CodeInput
              disabled={this.state.rendering}
              onRun={this.dbnRender.bind(this)}
            />

            {this.state.logLines.length > 0 &&
              <div className="mt-2 render-logs">
                {this.state.logLines.map((line, idx) => {
                  return (
                    <p key={idx}>
                      {line}
                    </p>
                  )
                })}
              </div>
            }

          </Col>
        </Row>
    )
  }
}

export default App;
