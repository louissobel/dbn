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
        <Col className="d-none d-md-block dbn-reference-index"  md={3} lg={3} xl={2}>
          <div className="sticky-top">
            <Index sectionList={sectionList} />
          </div>
        </Col>

        <Col sm={12} md={9} lg={7} className="dbn-reference-content">
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
                or changes in the blockchain. Note that using these <em>also</em> complicates
                your developer experience: the editing tool cannot fully simulate everything the blockchain does.
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
                <p>
                  There are multiple versions of the Ethereum blockchain running.
                  There's the real one, the <em>mainnet</em>, but there are also
                  various testnets. This tool is deployed both to the mainnet
                  and also to the Rinkeby testnet. Your code can detect
                  which blockchain it's running on using the <InlineCode>&lt;ChainID&gt;</InlineCode> number,
                  which will return <InlineCode number>4</InlineCode> on Rinkeby and <InlineCode number>1</InlineCode> on mainnet.
                </p>

              <h5>SHA3</h5>
                <p>
                  Cryptographic hash functions are an essential part of Ethereum,
                  the Keccak256 SHA-3 hash function particularly so. It is a core
                  operation exposed by the Ethereum Virtual Machine and is available
                  to use in your drawings via the <InlineCode>SHA3</InlineCode> number, which
                  takes one parameter. It returns the hash of the number interpreted as a 32-byte
                  two's complement big-endian integer.
                </p>

                <p>
                  An interesting use for <InlineCode>SHA3</InlineCode> is as a source of pseudo-randomness.
                  While true randomness is impossible to achieve using purely on-chain resources,
                  cryptographic hash functions are, by definition, seemingly random for a given input.
                  Try changing the input on line 8:
                </p>

                <InteractiveCodeAndImage example={Examples.sha3} />

              <h5>Call</h5>
                <p>
                  The final blockchain capability is one of the most powerful. Since your drawing will be deployed as a smart
                  contract it will be capable of calling the code of <em>other</em> smart contracts. The original DBN book
                  had the concept of <InlineCode>&lt;net&gt;</InlineCode> connectors, which this ability to is similar to in some ways.
                </p>

                <p>
                  Access other contracts through the <InlineCode>Call</InlineCode> number. It takes between two and eight parameters:
                </p>
                <ul>
                  <li>First, the address of the contract to call</li>
                  <li>
                    Second, the four byte <em>selector</em> of the function to call. The function selector is specified by Solidity to be the
                    first four bytes of the Keccak256 hash of the function signature.
                  </li>
                  <li>
                    Then up to six values can be passed
                  </li>
                </ul>

                <p>
                  Since DBN is not Solidity, there are clear limitations to this functionality. It only supports simple, 32-byte
                  parameters and return values. Functions must be referred to by the hash of their selector rather than by their name.
                  But it still offers a rudimentary way to build reactive drawings that change depending on the state of the blockchain.
                </p>

            </ReferenceSection>

            <ReferenceSection registerRef={registerSection()} name="Extras">
              <p>
                There's a few other extra / hidden features in this version of DBN.
              </p>

              <h5>Token ID</h5>
              <p>The <InlineCode>&lt;TokenID&gt;</InlineCode> number will return the id of your DBNFT (from 0–10200). In development, it will be zero.</p>

              <h5>Field</h5>
              <p>
                As a convenience (and to match capabilities in an existing reference DBN implementation), there is an additional command <InlineCode>Field</InlineCode>, that
                takes five parameters: <InlineCode>&lt;Field x0 y0 x1 y1 color&gt;</InlineCode>. It will draw a filled in rectangle
                of color <InlineCode>color</InlineCode> with one corner at <InlineCode>[x0 y0]</InlineCode> and
                the opposite one at <InlineCode>[x1 y1]</InlineCode>.
              </p>

              <InteractiveCodeAndImage example={Examples.field} />

              <h5>Hex Numbers</h5>
              <p>
                Most of the time, numbers are presented in base-10 form. <InlineCode number>64</InlineCode> means sixty-four. When dealing with large numbers
                on the blockchain however—like addresses and function selectors—it is often more convenient to read / write them in <em>hexadecimal</em>,
                or base-16, form. This version of DBN supports that via numbers prefixed with <InlineCode>0x</InlineCode>.
                In this form, <InlineCode number>0x64</InlineCode> does not mean sixty-four, but
                actually six-times-sixteen-plus-four, which is one hundred. Sixty-four would be represented by <InlineCode number>0x40</InlineCode>—four-times-sixteen.
              </p>

              <p>
                There's no need to ever use hexadecimal if you don't want to, but for dealing with things on the blockchain is it often easier to do so.
              </p>

              <h5>Modulo</h5>
              <p>
                Another additional math capability this version of DBN supports is modulo via the <InlineCode>%</InlineCode> operator, which returns
                what's left after division of the left and right values. For example, <InlineCode>(4 % 2)</InlineCode> is <InlineCode number>0</InlineCode>,
                and <InlineCode>((0 - 10209) % 101)</InlineCode> is <InlineCode number>-8</InlineCode>
              </p>

              <h5>Set Global</h5>
              <p>
                The DBN book, reasonably, does not go into detail about how variable <em>scoping</em> works in the DBN language. This version
                implements <em>dynamic scoping</em>. All variables have a default value of zero in a global environment. When trying to read a
                variable within a command or number, DBN first looks for it having been set within the most recent command or number. If that variable
                has not been set, DBN checks the caller, and so on recursively until the global environment is reached.
              </p>

              <p>
                When setting a variable, the value is stored in the environment of the current command or number. This approach provides a reasonably non-surprising experience,
                enables arbitrarily deep recursion, and unlocks optimizations (storing variables directly on the stack) when all variables are known to be local.
                However, it makes <em>one</em> example from the DBN book not work. This example implements a pseudo-random generator
                and expects a <InlineCode>Set</InlineCode> within a number to update the <em>global</em> value of that variable, not a value local to the number.
              </p>

              <p>
                To enable this (uncommon) use-case, this version of DBN supports a modified version of set: <InlineCode>Set Global</InlineCode>.
                This version of <InlineCode>Set</InlineCode> always updates the value of the variable in the global environment.
                Compare the below examples:
              </p>

              <InteractiveCodeAndImage example={Examples.setGlobalNotGlobal} />
              <InteractiveCodeAndImage example={Examples.setGlobalGlobal} />


              <h5>Log</h5>
              <p></p>

            </ReferenceSection>

          </div>
        </Col>
      </Row>
    </Container>
  )
}

export default Reference