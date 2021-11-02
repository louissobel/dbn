import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


import renderDBN from './dbn_renderer'
import CodeInput from './CodeInput'
import DBNImageResult from './DBNImageResult'


const MAX_MAGNIFICATION = 4

class DBNEditor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      imgURL : "",
      imageMagnify: 2,

      // 'INITIAL' | 'RENDERING' | 'ERROR' | 'DONE'
      renderState: 'INITIAL',

      bytecode: null,
      gasUsed: null,

      darkmode: false,

      renderError: null,
    };

  }

  maybeExtractDescription(code) {
    const firstLine = code.split("\n", 1)[0]
    const descriptionExtract = /^\/\/[Dd]escription: (.+)/
    const match = firstLine.match(descriptionExtract)
    if (match) {
      return match[1]
    } else {
      return null
    }
  }

  dbnRender(code) {
    this.setState({
      renderState: 'RENDERING',
      renderError: null,
      bytecode: null,
      description: null,
      imageData: null,
      gasUsed: null,
    })

    const renderOpts = {
      code: code,
      owningContract: process.env.REACT_APP_DBN_COORDINATOR_CONTRACT_ADDRESS,
    }
    const description = this.maybeExtractDescription(code)
    if (description) {
      renderOpts.description = description
      this.setState({description: description})
    }

    renderDBN(renderOpts, (update, data) => {
      switch(update) {
        case 'COMPILE_START':
          break;
        case 'COMPILE_END':
          break;
        case 'ASSEMBLE_START':
          break;
        case 'ASSEMBLE_END':
          this.setState({
            bytecode: data.result,
          })
          break;
        case 'INTERPRET_START':
          break;
        case 'INTERPRET_END':
          break;
        case 'INTERPRET_PROGRESS':
          if (data.imageData) {
            this.setState({
              imageData: data.imageData,
              gasUsed: data.gasUsed,
            })
          }
          break
        default:
          break;
      }
    })
    .then((result) => {
      console.log(result)
      this.setState({
        imageData: result.imageData,
        renderState: 'DONE',
        gasUsed: result.gasUsed,
      })
    })
    .catch((error) => {
      switch (error.type) {
        case 'parse':
        case 'compile':
          this.setState({
            renderState: 'ERROR',
            renderError: error,
          })
          break;
        default:
          console.error('unhandled error!', error)
          this.setState({renderState: 'ERROR'})
      }
    })
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

  onToggleDarkmode() {
    this.setState({
      darkmode: !this.state.darkmode,
    })
  }

  errorLines() {
    const out = [];
    if (!this.state.renderError) {
      return out
    }

    if (this.state.renderError.lineNumber) {
      out.push(this.state.renderError.lineNumber)
    }
    if (this.state.renderError.relatedLineNumber) {
      out.push(this.state.renderError.relatedLineNumber)
    }

    return out
  }

  render() {
    return (
      <Container>
        <Row className="pt-5">
          <Col sm={12} md={9} lg={6}>
            <DBNImageResult
              renderState={this.state.renderState}
              renderError={this.state.renderError}
              imageData={this.state.imageData}
              description={this.state.description}

              showMinter={true}
              minterEnabled={this.state.renderState === 'DONE'}

              bytecode={this.state.bytecode}
              gasUsed={this.state.gasUsed}
            />
          </Col>
          <Col sm={12} md={9} lg={6}>
            <CodeInput
              disabled={this.state.renderState === 'RENDERING'}
              onRun={this.dbnRender.bind(this)}
              errorLines={this.errorLines()}
            />
          </Col>
        </Row>
      </Container>
    )
  }
}

export default DBNEditor;