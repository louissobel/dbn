import React, {useState, useEffect} from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import renderDBN from '../render'
import ImageViewer from '../shared/ImageViewer'

import CodeMirror from '@uiw/react-codemirror';
import {lineNumbers} from "@codemirror/gutter"
import {dbnLanguage, dbnftHighlightStyle} from '../lang-dbn/dbn'

function SampleCodeAndImage({ className, code, noheaders, onAssemblyPresent, onBytecodePresent}) {
  //TODO: handle errors in here

  const [imageData, setImageData] = useState(null)

  useEffect(() => {
    renderDBN({code: code}, (e, d) => {
      if (e === 'INTERPRET_PROGRESS') {
        setImageData(d.imageData)
      }
      if (e === 'COMPILE_END') {
        if (onAssemblyPresent) {
          onAssemblyPresent(d.result)
        }
      }
      if (e === 'ASSEMBLE_END') {
        if (onBytecodePresent) {
          onBytecodePresent(d.result)
        }
      }
    })
    .then((r) => setImageData(r.imageData))
    .catch(error => console.error('', error))
  }, [code, onAssemblyPresent, onBytecodePresent]);
  

	return (
	  <Row className="dbn-sample-code-and-image">
      <Col xs={6} >
        {!noheaders && <h6>Input:</h6>}

        <div class="dbn-sample-code-wrapper">
          <CodeMirror
            value={code}
            extensions={[
              lineNumbers(),
              dbnLanguage,
              dbnftHighlightStyle,
            ]}
            autoFocus={false}
            editable={false}
            basicSetup={false}
          />
        </div>

      </Col>
      <Col xs={6} >
        {!noheaders && <h6>Output:</h6>}
        <ImageViewer imageData={imageData} magnify={1}/>
      </Col>
    </Row>
	)
}

export default SampleCodeAndImage