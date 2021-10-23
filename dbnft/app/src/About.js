import React, {useState, useEffect} from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ImageViewer from './ImageViewer'
import renderDBN from './dbn_renderer'

function About() {

  const [imageData, setImageData] = useState(null)

  const sampleCode = "Repeat X 0 100 {\n\
  Pen (100 - X)\n\
  Line X 0 X 100\n\
}"
  
  useEffect(() => {
    renderDBN({code: sampleCode}, (e, d) => {
      if (e === 'INTERPRET_PROGRESS') {
        setImageData(d.imageData)
      }
    })
    .then((r) => setImageData(r.imageData))
    .catch(error => console.error('', error))
  }, []);
  
  return (
    <Container>
      <Row className="pt-5" >
        <Col sm={12} md={9} lg={8} xl={6}>
          <div class="p-3 dbn-about-content">
            <h2>Design By Numbers NFT</h2>

            <p>
              Design By Numbers
                (<a target="_blank" href="https://dbn.media.mit.edu/whatisdbn.html">DBN</a>)
              is a programming language and environment
              developed by John Maeda in 1999 to help teach ideas about computation
              to designers and artists. It's fully documented in
              a <a target="_blank" href="https://mitpress.mit.edu/books/design-numbers">book</a> by the same name.
            </p>

            <p>
              The language allows users to draw in 101 levels of gray to a 101✕101 bitmap.
              There is basic support for variables, loops, conditionals, and user-defined-procedures.
            </p>

            <Row>
              <Col xs={6} >
                <h6>Input:</h6>
                <pre class="dbn-about-sample-code">
                  {sampleCode}
                </pre>
              </Col>
              <Col xs={6} >
                <h6>Output:</h6>
                <ImageViewer spinnerWhileEmpty={true} imageData={imageData} magnify={1}/>
              </Col>
            </Row>



          </div>
        </Col>

        <Col sm={12} md={9} lg={4} xl={6}>
          <div class="p-3 dbn-about-samples"  style={{backgroundColor: 'blue'}}>
            Gallery Wall
          </div>
        </Col>
      </Row>
    </Container>
  )
}

export default About