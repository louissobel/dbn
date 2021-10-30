import React, {useState, useEffect, useRef} from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { Link } from "react-router-dom";

import SampleCodeAndImage from './SampleCodeAndImage'
import InteractiveCodeAndImage from './InteractiveCodeAndImage'


function ReferenceSection({name, anchor, children}) {
  return (
    <div className="dbn-reference-section">
      <h3>{name}</h3>
      {children}
    </div>
  )
}

function InlineCode({ children }) {
  return (
    <span className="dbn-reference-inline-code">{children}</span>
  )
}


function Reference() {

  const editorRef = useRef()

  return (
    <Container>
      <Row>
        <Col className="d-none d-md-block"  md={4}>
          <div class="sticky-top" style={{backgroundColor: "red"}}>HI</div>
        </Col>

        <Col sm={12} md={8} lg={6}>
          <div className="p-2" style={{backgroundColor: "#ece9f5", height:3000}}>
            <ReferenceSection name="Line">
              <p>
                <InlineCode>Line</InlineCode>, followed by four
                values separated by a space will draw between 
                the two points specified.
              </p>

              <InteractiveCodeAndImage func='line' initialSpec={[
                {
                  type: 'constant',
                  value: "Line",
                },
                {
                  type: 'xcoord',
                  value: '0',
                  name: 'x0',
                },
                {
                  type: 'ycoord',
                  value: '0',
                  name: 'y0',
                },
                {
                  type: 'xcoord',
                  value: '100',
                  name: 'x1',
                },
                {
                  type: 'ycoord',
                  value: '100',
                  name: 'y1',
                }
              ]}/>


            </ReferenceSection>

            <ReferenceSection name="Paper">
              <p>
                <InlineCode>Paper</InlineCode> covers the whole image
                with the specified color.
              </p>

              <InteractiveCodeAndImage func='paper' initialSpec={[
                {
                  type: 'constant',
                  value: "Paper",
                },
                {
                  type: 'xcoord',
                  value: '0',
                  name: 'v',
                },
              ]}/>

              <SampleCodeAndImage code={"Line 0 0 100 100"} />
              <SampleCodeAndImage code={"Paper 50"} noheaders />
              <SampleCodeAndImage code={"Paper 100"} noheaders />

            </ReferenceSection>

            <ReferenceSection name="Pen"/>
            <ReferenceSection name="Variables"/>
            <ReferenceSection name="Repeat"/>
            <ReferenceSection name="Math"/>
            <ReferenceSection name="Set Dot"/>
            <ReferenceSection name="Get Dot"/>
            <ReferenceSection name="Questions"/>
            <ReferenceSection name="Commands"/>
            <ReferenceSection name="Numbers"/>
            <ReferenceSection name="Blockchain"/>
          </div>
        </Col>
      </Row>
    </Container>
  )
}

export default Reference