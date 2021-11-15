import React, {useState, useEffect, useReducer, useCallback, useRef} from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import classNames from 'classnames';


import InteractiveCodeAndImage from './InteractiveCodeAndImage'
import CanvasCoordinatesDemonstration from './CanvasCoordinatesDemonstration'
import Examples from './examples'


function ReferenceSection({name, registerRef, children, onMouseMove, onMouseLeave}) {
  let refCallback;
  if (registerRef) {
    refCallback = registerRef(name);
  }

  return (
    <div
      ref={refCallback}
      className="dbn-reference-section"
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
    >
      <h3>{name}</h3>
      {children}
    </div>
  )
}

function InlineCode({ number, children }) {
  return (
    <span
      className={classNames(
        "dbn-reference-inline-code",
        {number: !!number},
      )}
    >
      {children}
    </span>
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

function CanvasReferenceSection({ registerRef }) {
  const canvasRef = useRef()
  const [xCoord, setXCoord] = useState(null)
  const [yCoord, setYCoord] = useState(null)

  function mouseMove(e) {
    if (!canvasRef.current) {
      return
    }

    const canvasRect = canvasRef.current.getBoundingClientRect()

    let x = Math.min(100, Math.max(0, Math.floor((e.clientX - canvasRect.x) - 10)))
    setXCoord(x)

    let y = 100 - Math.min(100, Math.max(0, Math.floor((e.clientY - canvasRect.y) - 10)))
    setYCoord(y)

    // console.log(canvasRect, e.clientX, e.clientY)
    // console.log(x)
  }

  function mouseLeave(e) {
    setXCoord(null)
    setYCoord(null)
  }

  return (
    <ReferenceSection
      registerRef={registerRef}
      name="Canvas"
      onMouseMove={mouseMove}
      onMouseLeave={mouseLeave}
    >
      <p>
        You draw on a 101 by 101 pixel canvas, which starts out
        fully white. There are 10,201 points within this canvas.
        Each point is identified by
        two numbers, <InlineCode>x</InlineCode> and <InlineCode>y</InlineCode>,
        which range from 0 to 100 (inclusive).
      </p>

      <CanvasCoordinatesDemonstration
        canvasRef={canvasRef}
        x={xCoord}
        y={yCoord}
      />

    </ReferenceSection>

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

  const questionSameExample = useRef()
  const questionSmallerExample = useRef()

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

            <CanvasReferenceSection registerRef={registerSection()} />

            <ReferenceSection registerRef={registerSection()} name="Line">
              <p>
                You can draw a line between two points  
                using the command <InlineCode>Line</InlineCode>.
                The <InlineCode>x</InlineCode> and <InlineCode>y</InlineCode> coordinates
                of each point are passed as parameters.
              </p>

              <p>
                Try changing the example below to get a feel
                for it.
              </p>

              <InteractiveCodeAndImage example={Examples.line} />


            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Paper">
              <p>
                The command <InlineCode>Paper</InlineCode> covers the whole image
                with the color passed as a parameter. <InlineCode number>100</InlineCode> is
                black, <InlineCode number>0</InlineCode> is white,
                and there are 99 shades of gray between.
              </p>

              <InteractiveCodeAndImage example={Examples.paper} />


              <p>
                Note that <InlineCode>Paper</InlineCode> will cover anything that's
                already been drawn.
              </p>

              <InteractiveCodeAndImage example={Examples.paperCoveringLine} />
            </ReferenceSection>


            <ReferenceSection registerRef={registerSection()} name="Pen">
              <p>
                You can change the color of lines using the <InlineCode>Pen</InlineCode> command.
                The parameter passed will be the color of all subsequent lines drawn (until another call to <InlineCode>Pen</InlineCode>).
                The default value of pen is <InlineCode number>100</InlineCode>.
              </p>

              <InteractiveCodeAndImage example={Examples.simplePen}/>

              <p>
                Just these three commands—<InlineCode>Line</InlineCode>, <InlineCode>Paper</InlineCode>, and <InlineCode>Pen</InlineCode>—allow
                for a variety of drawings.
              </p>

              <InteractiveCodeAndImage example={Examples.pen}/>

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Variables">

              <p>
                Use the <InlineCode>Set</InlineCode> command to save a value to a variable.
                You can then use this variable anywhere you'd use a number.
              </p>

              <InteractiveCodeAndImage example={Examples.variables} />

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Repeat">
              <p>
                The <InlineCode>Repeat</InlineCode>  command will
                run code multiple times, with a specified variable
                set to a different value each time. It is passed three parameters:
                the name of a variable, the starting value, and the ending value.
                The code to actually repeat is surrounded by curly braces <InlineCode>{"{}"}</InlineCode>.
              </p>

              <InteractiveCodeAndImage example={Examples.repeat} />

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Comments">
              <p>
                As your code get more complicated, you can use comments
                (anything following a <InlineCode>//</InlineCode>) to make things
                more understandable.
              </p>

              <InteractiveCodeAndImage example={Examples.commentedLine} />

              <p>
                There is also a magic comment that, if it's the first line of the code,
                will give your drawing a title (stored as the description of the NFT).
              </p>
              <InteractiveCodeAndImage
                example={Examples.describedLine}
                titleImage="Line Example"
              />


            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Dots">
              <p>
                The 10,201 raw "dots"—pixels—of the canvas can be set and
                read directly by specifying a point wrapped in
                brackets, like <InlineCode>[x  y]</InlineCode>.
              </p>

              <InteractiveCodeAndImage example={Examples.dots} />

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Math">
              <p>
                You can use math operators to add (<InlineCode>+</InlineCode>),
                subtract (<InlineCode>-</InlineCode>),
                multiply (<InlineCode>*</InlineCode>),
                and divide (<InlineCode>/</InlineCode>) numbers or variables.
                Note that any math needs to be fully enclosed
                within parentheses.
              </p>


              <InteractiveCodeAndImage example={Examples.math} />
            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Questions">
              <p>
                Code can be run conditionally using <em>questions</em>.
                A question is given two parameters and will run the following <InlineCode>{"{}"}</InlineCode> enclosed
                block of code only if the answer is "yes".
              </p>

              <ul>
                <li><InlineCode>Same?</InlineCode>: if the two parameters are equal</li>
                <li><InlineCode>NotSame?</InlineCode>: if the two parameters are not equal</li>
                <li><InlineCode>Smaller?</InlineCode>: if the first parameters is smaller than the second</li>
                <li><InlineCode>NotSmaller?</InlineCode>: if the first parameters is not smaller than the second</li>
              </ul>

              <InteractiveCodeAndImage
                linkageRef={questionSameExample}
                linkedExample={questionSmallerExample}
                example={Examples.questionSame}
              />
              <InteractiveCodeAndImage
                linkageRef={questionSmallerExample}
                linkedExample={questionSameExample}
                example={Examples.questionSmaller}
              />
            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Commands">
              <p>
                You can define your own commands with the (fittingly named) command <InlineCode>Command</InlineCode>, followed
                by its name, then the names of any parameters,
                then the block of code to run each time the command is called.
              </p>

              <InteractiveCodeAndImage example={Examples.squareCommand} />

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Numbers">
              <p>
                Custom commands allow you to encapsulate drawing code. You can also
                encapsulate common math / computation using the
                command <InlineCode>Number</InlineCode>.
                Similar to <InlineCode>Command</InlineCode>, the
                command <InlineCode>Number</InlineCode> is passed the name of the new
                procedure, then the names of any parameters, then the block
                of code to run. Within the block, the command <InlineCode>Value</InlineCode> can
                be used to specify the result (without a <InlineCode>Value</InlineCode> command,
                the result will be <InlineCode number>0</InlineCode>)
              </p>

              <p>
                You can later use this new procedure anywhere you'd use a variable
                or a number by surrounding its name and any parameters
                in <InlineCode>&lt; &gt;</InlineCode> angle brackets.
              </p>

              <InteractiveCodeAndImage example={Examples.parabolaNumber} />

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Blockchain">
              <p>
                The original DBN book had a rich study of
                building <em>reactive</em> programs based off inputs from the mouse,
                keyboard, network, and so on. While those inputs are not available
                on the deterministic blockchain, the blockchain does offer its own
                unique capabilities that are exposed to DBN programs.
              </p>

              <p>
                Using these can make your drawing respond to its location
                or changes in the blockchain.
              </p>

              <h5>Time</h5>
                <p>
                  Each mined block in the Ethereum blockchain includes a
                  timestamp, which isn't necessarily the <em>exact</em> time
                  but will always be increasing and is roughly accurate.
                </p>

                <p>
                  You can access that time in your programs using the
                  built-in <InlineCode>Time</InlineCode> number. As in the
                  orginal DBN book, this number takes one parameter,
                  which should be <InlineCode number>1</InlineCode>, <InlineCode number>2</InlineCode>, or <InlineCode number>3</InlineCode>.
                </p>

                  <ul>
                    <li><InlineCode>&lt;Time 1&gt;</InlineCode>: hour from 0–23</li>
                    <li><InlineCode>&lt;Time 2&gt;</InlineCode>: minute from 0–59</li>
                    <li><InlineCode>&lt;Time 3&gt;</InlineCode>: second from 0–59</li>
                  </ul>

                <InteractiveCodeAndImage example={Examples.time} clock />

                <p>
                  Note that while in the above example, the image automatically
                  changes, that's not how the blockchain actually works. You
                  (or whoever is looking at your drawing) will need to call
                  your contract to re-render it to see it at a diffferent time.
                </p>

                {/*TODO: a way to simulate this in the editor? */}

              <h5>Address</h5>
                <p>
                  When you mint a DBNFT, you are also deploying your drawing
                  as a smart contract to the blockchain. You can access the
                  address your contract is deployed at using
                  the built-in number <InlineCode>&lt;Address&gt;</InlineCode> (which
                  requires no parameters).

                  {/*TODO: a way to simulate this in the editor? */}
                </p>

              <h5>Balance</h5>
                <p>
                  Another key aspect of the blockchain is how much Ethereum a
                  given address has. You can query this in your drawing using
                  the <InlineCode>&lt;Balance addr&gt;</InlineCode> number, which takes as its one
                  parameter a 20-byte address on the blockchain. It returns
                  the balance of that address in <em>wei</em>. A wei is the smallest
                  unit of Ethereum, like cents for dollars. 10<sup>18</sup> wei are
                  equivalent to one Ether.
                </p>

              <h5>Chain ID</h5>

              <h5>SHA3</h5>

              <h5>Call</h5>

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Extras">
              <ul>
                <li>token id</li>
                <li>hex numbers</li>
                <li>Modulo</li>
                <li>Field</li>
                <li>Log</li>
                <li>Set Global</li>
              </ul>
            </ReferenceSection>

          </div>
        </Col>
      </Row>
    </Container>
  )
}

export default Reference