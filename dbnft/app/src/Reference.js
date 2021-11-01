import React, {useState, useEffect, useRef} from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { Link } from "react-router-dom";

import SampleCodeAndImage from './SampleCodeAndImage'
import InteractiveCodeAndImage from './InteractiveCodeAndImage'
import CanvasCoordinatesDemonstration from './CanvasCoordinatesDemonstration'

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

            <ReferenceSection name="Canvas">
              <p>
                You draw on a 101x101 pixel canvas, which starts out
                fully white. There are 10201 points within this canvas,
                each of which is described by
                two numbers, <InlineCode>x</InlineCode> and <InlineCode>y</InlineCode>.
              </p>

              <CanvasCoordinatesDemonstration />

            </ReferenceSection>

            <ReferenceSection name="Line">
              <p>
                <InlineCode>Line</InlineCode>, followed by four
                values separated by a space will draw between 
                the two points specified.
              </p>

              <InteractiveCodeAndImage exampleFunc='line' initialSpec={[
                {value: "Line", type: 'constant'},
                {value: '0', name: 'x0', type: 'xcoord'},
                {value: '0', name: 'y0', type: 'ycoord'},
                {value: '100', name: 'x1', type: 'xcoord'},
                {value: '100', name: 'y1', type: 'ycoord'},
              ]}/>


            </ReferenceSection>

            <ReferenceSection name="Paper">
              <p>
                <InlineCode>Paper</InlineCode> covers the whole image
                with the specified color.
              </p>

              <InteractiveCodeAndImage exampleFunc='paper' initialSpec={[
                {value: 'Paper', type: 'constant'},
                {value: '100', type: 'color', name: 'v'}
              ]}/>

            </ReferenceSection>


            <ReferenceSection name="Pen">
              <p>
                <InlineCode>Pen</InlineCode> sets the color for subsequent
                Lines. It will stay in place until another call to Pen.
              </p>

              <InteractiveCodeAndImage exampleFunc='pen' initialSpec={[
                {value: "Paper", type: 'constant'},
                {value: '65', type: 'color', name: 'paper'},
                {value: '\n', type: 'constant'},
                {value: "Pen", type: 'constant'},
                {value: '10', type: 'color', name: 'pen1'},
                {value: '\n', type: 'constant'},
                {value: "Line", type: 'constant'},
                {value: '10', name: 'x01', type: 'xcoord'},
                {value: '10', name: 'y01', type: 'ycoord'},
                {value: '90', name: 'x11', type: 'xcoord'},
                {value: '90', name: 'y11', type: 'ycoord'},
                {value: '\n', type: 'constant'},
                {value: "Line", type: 'constant'},
                {value: '20', name: 'x02', type: 'xcoord'},
                {value: '10', name: 'y02', type: 'ycoord'},
                {value: '90', name: 'x12', type: 'xcoord'},
                {value: '80', name: 'y12', type: 'ycoord'},
                {value: '\n', type: 'constant'},
                {value: "Pen", type: 'constant'},
                {value: '90', type: 'color', name: 'pen2'},
                {value: '\n', type: 'constant'},
                {value: "Line", type: 'constant'},
                {value: '0', name: 'x03', type: 'xcoord'},
                {value: '100', name: 'y03', type: 'ycoord'},
                {value: '100', name: 'x13', type: 'xcoord'},
                {value: '0', name: 'y13', type: 'ycoord'},
              ]}/>
            </ReferenceSection>

            <ReferenceSection name="Variables">

              <p>
                Use the <InlineCode>Set</InlineCode> command to save a value to a variable,
                which can then be used later wherever you'd use a number.
              </p>

              <InteractiveCodeAndImage exampleFunc='variable' initialSpec={[
                {value: "Set X", type: 'constant'},
                {value: "50", type: 'xcoord', name: 'xval'},
                {value: '\n', type: 'constant'},
                {value: "Line", type: 'constant'},
                {value: 'X', type: 'constant'},
                {value: '0', name: 'y0', type: 'ycoord'},
                {value: 'X', type: 'constant'},
                {value: '100', name: 'y1', type: 'ycoord'},
              ]}/>

            </ReferenceSection>

            <ReferenceSection name="Repeat">
              The <InlineCode>Repeat</InlineCode> will
              run code multiple times, with a specified variable
              set to a different value each time.

              <InteractiveCodeAndImage exampleFunc='repeat' initialSpec={[
                {value: 'Repeat X', type: 'constant'},
                {value: '25', name: 'start', type: 'xcoord'},
                {value: '75', name: 'end', type: 'xcoord'},
                {value: '{', type: 'constant'},
                {value: '\n', type: 'constant'},
                {value: '  Pen X', type: 'constant'},
                {value: '\n', type: 'constant'},
                {value: "  Line", type: 'constant'},
                {value: 'X', type: 'constant'},
                {value: '0', name: 'y0', type: 'ycoord'},
                {value: 'X', type: 'constant'},
                {value: '100', name: 'y1', type: 'ycoord'},
                {value: '\n', type: 'constant'},
                {value: '}', type: 'constant'},
              ]} />

            </ReferenceSection>

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