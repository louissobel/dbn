import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


import renderDBN from './dbn_renderer'
import CodeInput from './CodeInput'
import DBNImageResult from './DBNImageResult'

import {SessionStorage} from './storage'
import {maybeExtractDescription} from './lang-dbn/dbn.js'

const MAX_MAGNIFICATION = 4
const DEFAULT_INITIAL_CODE = `//description: a line\n\nLine 0 0 100 100`


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

    if (!SessionStorage.enabled) {
      console.warn('sessionStorage is not enabled, cannot persist code across refreshes');
      this.codeStorageKey = null;
    } else {
      this.codeStorageKey = 'dbnft.io–primary-editor-code';
    }

    this.initialCode = this.getInitialCode()
  }

  dbnRender(code) {
    if (this.state.renderState === 'RENDERING') {
      console.warn('render request while render in progress...')
      return;
    }

    let cancelSignal = new Promise((resolve) => {
      this.renderCancelTrigger = resolve;
    })

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
    const description = maybeExtractDescription(code)
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
    }, cancelSignal)
    .then((result) => {
      console.log(result)
      this.setState({
        imageData: result.imageData,
        renderState: 'DONE',
        gasUsed: result.gasUsed,
      })
    })
    .catch((error) => {
      if (error.type) {
        this.setState({
          renderState: 'ERROR',
          renderError: error,
        })
      } else {
        console.error('error without type!', error)
        this.setState({renderState: 'ERROR'})
      }
    })
  }

  cancelRender() {
    if (this.state.renderState !== 'RENDERING') {
      console.warn('how can we cancel render if we are not in render state?')
      return;
    }
    if (!this.renderCancelTrigger) {
      throw new Error('we are rendering, but no cancel trigger present!')
    }
    this.renderCancelTrigger()
  }

  onCodeChange(code) {
    this.saveCodeToSessionStorageIfEnabled(code)
  }

  saveCodeToSessionStorageIfEnabled(code) {
    if (SessionStorage.enabled) {
      SessionStorage.get().setItem(
        this.codeStorageKey,
        code,
      )
    }
  }

  getInitialCode() {
    if (SessionStorage.enabled) {
      let restored = SessionStorage.get().getItem(this.codeStorageKey);
      if (restored) {
        console.log('Restored code from sessionStorage')
        return restored;
      } else {
        return DEFAULT_INITIAL_CODE; 
      }
    } else {
      return DEFAULT_INITIAL_CODE;
    }
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
              onCancel={this.cancelRender.bind(this)}
            />
          </Col>
          <Col sm={12} md={9} lg={6}>
            <CodeInput
              initialCode={this.initialCode}
              disabled={this.state.renderState === 'RENDERING'}
              onRun={this.dbnRender.bind(this)}
              onChange={this.onCodeChange.bind(this)}
              errorLines={this.errorLines()}
            />
          </Col>
        </Row>
      </Container>
    )
  }
}

export default DBNEditor;