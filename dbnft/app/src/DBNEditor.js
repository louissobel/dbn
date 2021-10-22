import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Accordion from 'react-bootstrap/Accordion';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import { Icon } from '@iconify/react';

import {evmAssemble, evmInterpret} from './evm_tools'
import renderDBN from './dbn_renderer'
import CodeInput from './CodeInput'
import ImageViewer from './ImageViewer'
import DBNFTMinter from './DBNFTMinter'

const MAX_MAGNIFICATION = 4

class DBNEditor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rendering: false,
      logLines: [],
      imgURL : "",
      imageMagnify: 2,
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

  dbnRender2(code) {
    this.setState({
      rendering: true,
      logLines: [],
      bytecode: null,
      imageData: null,
    })

    renderDBN(code, (update, data) => {
      switch(update) {
        case 'COMPILE_START':
          this.addLogLine("Compiling...")
          break;
        case 'COMPILE_END':
          this.finishLogLine("OK!")
          break;
        case 'ASSEMBLE_START':
          this.addLogLine("Assembling...")
          break;
        case 'ASSEMBLE_END':
          this.finishLogLine("OK!")
          this.setState({
            bytecode: data.result,
          })
          break;
        case 'INTERPRET_START':
          this.addLogLine("Interpreting...")
          break;
        case 'INTERPRET_END':
          this.finishLogLine("OK!")
          break;
        case 'INTERPRET_PROGRESS':
          if (data.imageData) {
            this.setState({
              imageData: data.imageData,
            })
          }
          break
      }
    })
    .then((imageData) => {
      this.setState({
        imageData: imageData,
        rendering: false,
      })
    })
    .catch((error) => {
      this.finishLogLine(error)
      console.error('', error)
      this.setState({rendering: false})
    })
  }

  dbnRender(code) {
    this.setState({
      rendering: true,
      logLines: [],
      bytecode: null,
      imageData: null,
    }, () => {
      this.addLogLine("Compiling... ")
    })
    
    fetch(this.props.compilePath, {
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
      this.setState({bytecode: bytecode})

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
      const bitmapBlob = new Blob([result.returnValue], {type: 'image/bmp'})

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

  canZoomIn() {
    return this.state.imageMagnify < MAX_MAGNIFICATION;
  }

  canZoomOut() {
    return this.state.imageMagnify > 1;
  }

  zoomUpdate(change) {
    this.setState({
      imageMagnify: this.state.imageMagnify + change,
    });
  }

  onPixelHover(data) {
    this.setState({
      hoveringOverPixel: data,
    })
  }

  render() {
    return (
      <Container>
        <Row className="pt-5">
          <div class="dbn-editor-control-bar">
            <ButtonGroup  aria-label="Basic example">
              <Button variant="light" disabled={!this.canZoomOut()} onClick={this.zoomUpdate.bind(this, -1)}>
                <Icon icon="oi:zoom-out" inline={true} />
              </Button>

              <Button variant="light" disabled={!this.canZoomIn()} onClick={this.zoomUpdate.bind(this, +1)}>
                <Icon icon="oi:zoom-in" inline={true}/>
              </Button>

              <Button variant="light" className="zoom-indicator" disabled={true}>
                {this.state.imageMagnify + "x"}
              </Button>
            </ButtonGroup>

            {/*{this.state.hoveringOverPixel &&*/}
              <div className="d-inline-block mx-2">
                <span class="badge rounded-pill bg-light text-dark ms-1">
                  X: {this.state.hoveringOverPixel?.x}
                </span>
                <span class="badge rounded-pill bg-light text-dark ms-1">
                  Y: {this.state.hoveringOverPixel?.y}
                </span>
                <span class="badge rounded-pill bg-light text-dark ms-1">
                  Dot: {this.state.hoveringOverPixel?.color}
                </span>
              </div>
            {/*}*/}
          </div>

          <Col>
            <div class="dbn-image-result">
              <div className="mx-auto dbn-image-viewer" style={{width: 101*MAX_MAGNIFICATION }}>
                <ImageViewer
                  imageData={this.state.imageData}
                  magnify={this.state.imageMagnify}
                  onPixelHover={this.onPixelHover.bind(this)}
                  extraClass="mx-auto"
                />
              </div>

              {/*
                TODO: get a standard view of where we are in the render process
                To avoid race conditions and such.....
              */}
              {this.state.bytecode && this.state.imageData &&
                <DBNFTMinter
                  bytecode={this.state.bytecode}
                  imageData={this.state.imageData}
                />
              }

            </div>
          </Col>
          <Col>
            <CodeInput
              disabled={this.state.rendering}
              onRun={this.dbnRender2.bind(this)}
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
      </Container>
    )
  }
}

export default DBNEditor;