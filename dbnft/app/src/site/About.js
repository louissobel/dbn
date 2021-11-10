import React, {useState} from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { Link } from "react-router-dom";

import SampleCodeAndImage from './SampleCodeAndImage'

function About() {

  const [assemblyCode, setAssemblyCode] = useState(null)
  const [bytecode, setBytecode] = useState(null)

  const sampleCode = 
`Repeat X 0 100 {
  Pen X\n\
  Line X 0 X 100\n\
}`
  
  return (
    <Container>
      <Row className="pt-2 dbn-about-body" >
        <Col sm={12} md={9} lg={8} xl={7}>
          <div class="p-3 dbn-about-content">
            <h2>Design By Numbers NFT</h2>
            <h6><em>Create on-chain NFTs by deploying smart contracts that render images</em></h6>

            <p>
              Design By Numbers
                (<a target="_blank" rel="noreferrer" href="https://dbn.media.mit.edu/whatisdbn.html">DBN</a>)
              is a programming language and environment
              developed by John Maeda in 1999 to help teach ideas about computation
              to designers and artists. It's fully documented in
              a <a target="_blank" rel="noreferrer" href="https://mitpress.mit.edu/books/design-numbers">book</a> by the same name.
            </p>

            <p>
              The language allows people to draw in 101 levels of gray to a 101✕101 bitmap.
              There is basic support for variables, loops, conditionals, and user-defined-procedures.
            </p>

            <SampleCodeAndImage
              code={sampleCode}
              onAssemblyPresent={setAssemblyCode}
              onBytecodePresent={setBytecode}
            />

            <h4>NFT</h4>

            <p>
              This tool enables you to create NFTs by compiling DBN code directly to a smart contract that
              can render itself as a bitmap. There is no Solidity involved in this step, just DBN and raw EVM Opcodes.
            </p>

            <h6>The above code becomes:</h6>
            <pre class="dbn-about-sample-code" style={{height: "100px"}}>
              {assemblyCode}
            </pre>

            <h6>Which is then turned into:</h6>
            <pre class="dbn-about-sample-code" style={{height: "100px"}}>
              {bytecode}
            </pre>

            <p>
              Minting a DBNFT involves <em>deploying</em> your drawing as a smart contract
              to the Ethereum blockchain. When it's time to get the image for the NFT,
              that smart contract is called and a bitmap image is created and returned.
            </p>
          </div>
        </Col>

        <Col sm={12} md={12} lg={4} xl={5}>
          <Row className="p-3">
            <div className="mt-3 p-3 dbn-about-get-started text-white">
                <h4>Start Creating:</h4>
                <p>
                  <ul>
                    <li>
                      <Link className="text-white" to="/create">Editor</Link>
                    </li>
                    <li>
                      <Link className="text-white" to="/reference">Language Reference</Link>
                    </li>
                    <li>
                      <Link className="text-white" to="/gallery">Gallery</Link>
                    </li>
                  </ul>

                </p>
            </div>
          </Row>
          <Row className="p-3">
            <div style={{backgroundColor: "blue"}} >
            </div>
          </Row>

        </Col>
      </Row>
    </Container>
  )
}

export default About