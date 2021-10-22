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
import DBNEditorControlBar from './DBNEditorControlBar'
import DBNFTMinter from './DBNFTMinter'
import DBNEditorRenderStatus from './DBNEditorRenderStatus'

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
    };

  }

  dbnRender(code) {
    this.setState({
      renderState: 'RENDERING',
      bytecode: null,
      imageData: null,
      gasUsed: null,
    })

    renderDBN(code, (update, data) => {
      console.log(update)
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
      }
    })
    .then((result) => {
      console.log("result")
      this.setState({
        imageData: result.imageData,
        renderState: 'DONE',
        gasUsed: result.gasUsed,
      })
    })
    .catch((error) => {
      console.error('', error)
      this.setState({renderState: 'ERROR'})
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

  render() {
    return (
      <Container>
        <Row className="pt-5">
          <Col>
            <div className={"dbn-image-result " + (this.state.darkmode ? "darkmode" : "")}>
              <DBNEditorControlBar
                canZoomIn={this.canZoomIn()}
                onZoomIn={this.zoomUpdate.bind(this, 1)}
                canZoomOut={this.canZoomOut()}
                onZoomOut={this.zoomUpdate.bind(this, -1)}
                magnfication={this.state.imageMagnify}

                hoverX={this.state.hoveringOverPixel?.x}
                hoverY={this.state.hoveringOverPixel?.y}
                hoverColor={this.state.hoveringOverPixel?.color}

                onToggleDarkmode={this.onToggleDarkmode.bind(this)}
                darkmode={this.state.darkmode}

              />

              <div className="mx-auto dbn-image-viewer" style={{width: 101*MAX_MAGNIFICATION }}>
                <ImageViewer
                  imageData={this.state.imageData}
                  magnify={this.state.imageMagnify}
                  onPixelHover={this.state.renderState !== 'INITIAL' &&
                    this.onPixelHover.bind(this)
                  }
                  extraClass="mx-auto"
                />
              </div>


              <div className="mx-auto dbn-image-mint-controls">
                <DBNFTMinter
                  disabled={this.state.renderState !== 'DONE'}
                  bytecode={this.state.bytecode}
                  imageData={this.state.imageData}
                />
              </div>

              <DBNEditorRenderStatus
                renderState={this.state.renderState}
                codeSize={this.state.bytecode ? (this.state.bytecode.length - 2)/2 : null}
                gasUsed={this.state.gasUsed}
                darkmode={this.state.darkmode}
              />

            </div>
          </Col>
          <Col>
            <CodeInput
              disabled={this.state.renderState === 'RENDERING'}
              onRun={this.dbnRender.bind(this)}
            />
          </Col>
        </Row>
      </Container>
    )
  }
}

export default DBNEditor;