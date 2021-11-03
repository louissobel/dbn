import React, {useState, useEffect, useReducer, useCallback} from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import classNames from 'classnames';


import InteractiveCodeAndImage from './InteractiveCodeAndImage'
import CanvasCoordinatesDemonstration from './CanvasCoordinatesDemonstration'

function ReferenceSection({name, registerRef, children}) {
  let refCallback;
  if (registerRef) {
    refCallback = registerRef(name);
  }

  return (
    <div ref={refCallback} className="dbn-reference-section">
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

function Index({ sectionList }) {
  const [activeItem, setActiveItem] = useState(0)
  const [autoscrollingTimeout, setAutoscrollingTimeout] = useState(null)

  const clickHandler = function(node, i) {
    return function() {
      if (autoscrollingTimeout) {
        // clear the current one and set a new one
        clearTimeout(autoscrollingTimeout)
      }
      setAutoscrollingTimeout(setTimeout(() => {
        setAutoscrollingTimeout(null)
      }, 1000))

      node.scrollIntoView();
      

      setActiveItem(i);
    }
  }

  const scrollHandler = useCallback(function(e) {
    // go through our sections and see which are in view...
    if (autoscrollingTimeout) {
      return;
    }

    for (let i = 0; i<sectionList.length; i++) {
      let section = sectionList[i]
      let visible = section.node.getBoundingClientRect().bottom > 101;
      if (visible) {
        setActiveItem(i);
        break;
      }
    }
  }, [sectionList, autoscrollingTimeout])

  useEffect(() => {
    window.addEventListener('scroll', scrollHandler)
    return function() {
      window.removeEventListener('scroll', scrollHandler);
    }
  }, [scrollHandler])

  const nodes = sectionList.map(({name, node}, i) => {
    let active = i === activeItem
    return (
      <div className={classNames("p-1", "dbn-reference-index-item", {'active-section': active})}>
        <h5 onClick={clickHandler(node, i)}>
          {name}
        </h5>
      </div>
    )
  })

  return (
    <>
      {nodes}
    </>
  )
}


function Reference() {
  const [sectionList, dispatch] = useReducer((initialSectionList, action) => {
    let currentData = initialSectionList[action.index];

    if (!currentData || currentData.node !== action.node) {
      let newSectionList = initialSectionList.slice();
      newSectionList[action.index] = {name: action.name, node: action.node}
      return newSectionList
    } else {
      return initialSectionList
    }
  }, [])

  var sectionCount = 0;
  const nextSectionIndex = function() {
    let out = sectionCount;
    sectionCount++
    return out;
  }

  const registerSection = function() { 
    let index = nextSectionIndex();

    return function (name) {
      return function(node) {
        // ignore unmounts
        if (node) {
          dispatch({index: index, name: name, node: node})
        }
      }
    }
  }

  return (
    <Container>
      <Row>
        <Col className="d-none d-lg-block" lg={1} xl={2}></Col>
        <Col className="d-none d-md-block dbn-reference-index"  md={4} lg={3} xl={2}>
          <div className="sticky-top">
            <Index sectionList={sectionList} />
          </div>
        </Col>

        <Col sm={12} md={8} lg={6} className="dbn-reference-content">
          <div className="p-2" >

            <ReferenceSection registerRef={registerSection()} name="Canvas">
              <p>
                You draw on a 101x101 pixel canvas, which starts out
                fully white. There are 10201 points within this canvas,
                each of which is described by
                two numbers, <InlineCode>x</InlineCode> and <InlineCode>y</InlineCode>.
              </p>

              <CanvasCoordinatesDemonstration />

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Line">
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

            <ReferenceSection registerRef={registerSection()} name="Paper">
              <p>
                <InlineCode>Paper</InlineCode> covers the whole image
                with the specified color.
              </p>

              <InteractiveCodeAndImage exampleFunc='paper' initialSpec={[
                {value: 'Paper', type: 'constant'},
                {value: '100', type: 'color', name: 'v'}
              ]}/>

            </ReferenceSection>


            <ReferenceSection registerRef={registerSection()} name="Pen">
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

            <ReferenceSection registerRef={registerSection()} name="Variables">

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

            <ReferenceSection registerRef={registerSection()} name="Repeat">
              <p>
                The <InlineCode>Repeat</InlineCode> will
                run code multiple times, with a specified variable
                set to a different value each time.
              </p>

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

            <ReferenceSection registerRef={registerSection()} name="Math"/>
            <ReferenceSection registerRef={registerSection()} name="Set Dot"/>
            <ReferenceSection registerRef={registerSection()} name="Get Dot"/>
            <ReferenceSection registerRef={registerSection()} name="Questions"/>
            <ReferenceSection registerRef={registerSection()} name="Commands"/>
            <ReferenceSection registerRef={registerSection()} name="Numbers"/>
            <ReferenceSection registerRef={registerSection()} name="Blockchain"/>
          </div>
        </Col>
      </Row>
    </Container>
  )
}

export default Reference