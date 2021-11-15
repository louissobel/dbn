import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';
import Modal from 'react-bootstrap/Modal';


import ImageResult from '../image_result/ImageResult'
import MintStatusAlert from '../minter/MintStatusAlert'
import renderDBN from '../render'
import {SessionStorage, STORAGE_KEY_RESET_INITIAL_CODE} from '../storage'
import {maybeExtractDescription, maybeExtractConfig} from '../lang-dbn/dbn.js'
import CodeInput from './CodeInput'

import frontendEnvironment from '../frontend_environment'


const MAX_MAGNIFICATION = 4
const DEFAULT_INITIAL_CODE = `//description: a line\n\nLine 0 0 100 100`
const DBNFT_PRIMARY_CODE_SESSION_STORAGE_KEY = 'dbnft.io–primary-editor-code'


// Work around where SessionStorage is copied even when we're
// explicitly trying to open a new window with new code
if (SessionStorage.enabled) {
  let resetInitialCode = !!SessionStorage.get().getItem(STORAGE_KEY_RESET_INITIAL_CODE);
  if (resetInitialCode) {
    SessionStorage.get().removeItem(STORAGE_KEY_RESET_INITIAL_CODE)
    SessionStorage.get().removeItem(DBNFT_PRIMARY_CODE_SESSION_STORAGE_KEY)
  }
}

class Editor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      imgURL : "",
      imageMagnify: 2,

      // 'INITIAL' | 'RENDERING' | 'ERROR' | 'DONE'
      renderState: 'INITIAL',

      bytecode: null,
      assemblyCode: null,
      lastRenderedCode: null,
      gasUsed: null,

      darkmode: false,

      renderError: null,

      mintsInProgress: [],

      showCodeModal: false,
    };
    this._mintEventEmitters = {}

    if (!SessionStorage.enabled) {
      console.warn('sessionStorage is not enabled, cannot persist code across refreshes');
      this.codeStorageKey = null;
    } else {
      this.codeStorageKey = DBNFT_PRIMARY_CODE_SESSION_STORAGE_KEY;
    }

    this.initialCode = this.getInitialCode()
  }

  
  onMintInProgress = (transactionHash, mintEventEmitter) => {
    this._mintEventEmitters[transactionHash] = mintEventEmitter

    if (!this.state.mintsInProgress.includes(transactionHash)) {
      let newMintsInProgress = this.state.mintsInProgress.concat([transactionHash])
      this.setState({
        mintsInProgress: newMintsInProgress,
      })
    }
  }

  removeInProgressMint(transactionHashToRemove) {
    console.log(transactionHashToRemove)
    let newMintsInProgress = []
    this.state.mintsInProgress.forEach((transactionHash) => {
      if (transactionHash !== transactionHashToRemove) {
        newMintsInProgress.push(transactionHash)
        console.log(transactionHash);
      }
    })
    this.setState({
      mintsInProgress: newMintsInProgress,
    }, () => {
      delete this._mintEventEmitters[transactionHashToRemove]
    })
  }

  onMintabilityStatusChange = (status) => {
    this.setState({mintabilityStatus: status})
  } 

  onShowCode = () => {
    this.setState({showCodeModal: true})
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
      assemblyCode: null,
      lastRenderedCode: code,
      description: null,
      imageData: null,
      gasUsed: null,
    })

    const codeConfig = maybeExtractConfig(code)

    const renderOpts = {
      code: code,
      useHelpers: !codeConfig.nohelpers && frontendEnvironment.config.useHelpers,
      helperAddress: frontendEnvironment.config.helperAddress,
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
        case 'LINK_END':
          this.setState({
            assemblyCode: data.result,
          })
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
        case 'LOG':
          console.log(`Line ${data.lineNo}: 0x${data.value}`)
          break;
        default:
          break;
      }
    }, cancelSignal)
    .then((result) => {
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
      }
    }

    // Check the URL
    let searchParams = new URLSearchParams(window.location.search);
    let initialCode = searchParams.get('initialCode');
    if (initialCode) {
      return initialCode
    }

    // ok, fall back
    return DEFAULT_INITIAL_CODE; 
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

  topInfoRow() {
    // only shown sometimes
    const anyMintsInProgress = this.state.mintsInProgress.length > 0

    const mintabilityNotice = this.state.mintabilityStatus === 'NOT_ALLOWLISTED';

    const show = anyMintsInProgress || mintabilityNotice;

    if (!show) {
      return null
    }

    let mintStatus = this.state.mintsInProgress.map((transactionHash) => {
      return <MintStatusAlert
        key={transactionHash}
        transactionHash={transactionHash}
        mintEventEmitter={this._mintEventEmitters[transactionHash]}
        onClose={this.removeInProgressMint.bind(this, transactionHash)}
      />
    })

    return (
      <Row className="pt-3 justify-content-md-center">
        <Col md={12} lg={9} xl={6}>

          {mintStatus}

          {mintabilityNotice &&
            <Alert variant="warning">
              Minting is currently limited. You can still work on drawings
              and learn the DBN language! Follow @__ for updates on when minting will
              open up or to request access to mint.
            </Alert>
          }

        </Col>
      </Row>
    )    

  }

  render() {
    return (
      <Container>
        {this.topInfoRow()}


        <Row className="pt-5">
          <Col sm={12} md={9} lg={6}>
            <ImageResult
              renderState={this.state.renderState}
              renderError={this.state.renderError}
              imageData={this.state.imageData}
              description={this.state.description}
              settingsStorageKey={'primary-editor'}

              showMinter={true}
              minterEnabled={this.state.renderState === 'DONE'}
              onMintInProgress={this.onMintInProgress}
              onMintabilityStatusChange={this.onMintabilityStatusChange}

              bytecode={this.state.bytecode}
              code={this.state.lastRenderedCode}
              onShowCode={this.onShowCode}
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


        <Modal
          show={this.state.showCodeModal}
          size="lg"
          onHide={() => this.setState({showCodeModal: false})}
          className="dbn-show-code-modal"
        >
          <Modal.Header closeButton={true}>
            <Modal.Title>Assembly & Bytecode</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <h6>Assembly</h6>
            <pre className="dbn-low-level-code" style={{maxHeight:400}}>{this.state.assemblyCode}</pre>

            <h6>Bytecode</h6>
            <pre className="dbn-low-level-code wordwrap">{this.state.bytecode}</pre>
          </Modal.Body>
        </Modal>

      </Container>
    )
  }
}

export default Editor;
