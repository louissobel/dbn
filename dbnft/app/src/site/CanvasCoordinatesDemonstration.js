import React, {useEffect} from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';


// RGB for the "guidebar" to appear showing what's moving in Line
const GUIDEBAR_COLOR = [0x1b, 0x1b, 0xac]

function CanvasCoordinatesDemonstration({ x, y, canvasRef }) {

  useEffect(() => {
    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d')

    ctx.clearRect(0, 0, 121, 121)

    ctx.fillStyle = 'white';
    ctx.fillRect(10, 10, 101, 101)

    let guidePixel = ctx.createImageData(1, 1);
    guidePixel.data[0] = GUIDEBAR_COLOR[0]
    guidePixel.data[1] = GUIDEBAR_COLOR[1]
    guidePixel.data[2] = GUIDEBAR_COLOR[2]
    guidePixel.data[3] = 255;

    if (y !== null) {
      for (let x = 0; x<121; x++) {
        ctx.putImageData(guidePixel, x, 120 - (y + 10))
      }
    }

    if (x !== null) {
      for (let y = 0; y<121; y++) {
        ctx.putImageData(guidePixel, (x + 10), y)
      }
    }


    // axis ticks, X
    for (let xTick of [0, 100]) {
      for (let xTickY = 111; xTickY<121; xTickY++) {
        ctx.putImageData(guidePixel, xTick+10, xTickY)
      }      
    }


    // axis ticks, Y
    for (let yTick of [10, 110]) {
      for (let yTickX = 0; yTickX<10; yTickX++) {
        ctx.putImageData(guidePixel, yTickX, yTick)
      }      
    }

  }, [x, y, canvasRef])

  return (

    <Row className="dbn-reference-code-and-image">
      <Col>
        <div style={{position: 'relative', width:121}} className='mx-auto'>
          <canvas
            ref={canvasRef}
            height={121}
            width={121}
            // onMouseMove={canvasMouseOver}
            // onMouseLeave={canvasMouseOut}
            style={{
              position: 'relative',
              top:'-10px',
              left: '-10px',
              cursor: 'crosshair',
            }}
          />

          <div style={{
            position: 'absolute',
            textAlign: 'center',
            width: 101,
            top:'calc(100px + 1rem)',
            left: 0,
            lineHeight:'1rem',
          }}>
            <span className="dbn-reference-inline-code">
              {(x === null) ? 'x' : 'x: ' + x}
            </span>
          </div>

         <div style={{
            position: 'absolute',
            textAlign: 'right',
            height: 101,
            width: '100px',
            lineHeight: '101px',
            top: 0,
            left: 'calc(-100px - 1.5rem)',
          }}>
            <span className="dbn-reference-inline-code">
              {(y === null) ? 'y' : 'y: ' + y}
            </span>
          </div>

         <div style={{
            position: 'absolute',
            textAlign: 'center',
            width: '20px',
            top: 112,
            lineHeight:'1rem',
            left: -10,

          }}>
            <span className="dbn-reference-canvas-example-label">0</span>
          </div>

         <div style={{
            position: 'absolute',
            textAlign: 'center',
            width: '20px',
            top: 112,
            lineHeight:'1rem',
            left: 90,

          }}>
            <span className="dbn-reference-canvas-example-label">100</span>
          </div>

         <div style={{
            position: 'absolute',
            textAlign: 'right',
            width: '20px',
            top: 100,
            lineHeight: 0,
            left: 'calc(-22px - 1em)',
          }}>
            <span className="dbn-reference-canvas-example-label">0</span>
          </div>

         <div style={{
            position: 'absolute',
            textAlign: 'right',
            width: '20px',
            top: 0,
            lineHeight: 0,
            left: 'calc(-22px - 1em)',
          }}>
            <span className="dbn-reference-canvas-example-label">100</span>
          </div>

        </div>
      </Col>
    </Row>
  )
}

export default CanvasCoordinatesDemonstration
