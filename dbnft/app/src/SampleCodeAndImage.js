import React, {useState, useEffect} from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import renderDBN from './dbn_renderer'
import ImageViewer from './ImageViewer'


function SampleCodeAndImage({ className, code, noheaders, onAssemblyPresent}) {
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
    })
    .then((r) => setImageData(r.imageData))
    .catch(error => console.error('', error))
  }, [code, onAssemblyPresent]);
  

	return (
	  <Row className="dbn-sample-code-and-image">
      <Col xs={6} >
        {!noheaders && <h6>Input:</h6>}
        <pre class="dbn-about-sample-code">
          {code}
        </pre>
      </Col>
      <Col xs={6} >
        {!noheaders && <h6>Output:</h6>}
        <ImageViewer imageData={imageData} magnify={1}/>
      </Col>
    </Row>
	)
}

export default SampleCodeAndImage