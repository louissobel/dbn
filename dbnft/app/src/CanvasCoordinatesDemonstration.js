import React, {useState, useEffect, useRef} from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';


// RGB for the "guidebar" to appear showing what's moving in Line
const GUIDEBAR_COLOR = [0x1b, 0x1b, 0xac]

function CanvasCoordinatesDemonstration({ func, initialSpec }) {
  const canvasRef = useRef()

  const [xCoord, setXCoord] = useState(50)
  const [yCoord, setYCoord] = useState(50)

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

    for (let x = 0; x<121; x++) {
      ctx.putImageData(guidePixel, x, 120 - (yCoord + 10))
    }
    for (let y = 0; y<121; y++) {
      ctx.putImageData(guidePixel, (xCoord + 10), y)
    }
  }, [xCoord, yCoord])

  function canvasMouseOver(e) {
    const canvasX = Math.min(120, Math.max(e.nativeEvent.offsetX, 0))
    const canvasY = Math.min(120, Math.max(e.nativeEvent.offsetY, 0))

    const offsetX = Math.min(100, Math.max(canvasX - 10, 0))
    const offsetY = Math.min(100, Math.max((120 - canvasY) - 10, 0))

    setXCoord(offsetX)
    setYCoord(offsetY)
  }

  function canvasMouseOut(e) {
    setXCoord(50)
    setYCoord(50)
  }

  return (

    <Row className="dbn-reference-code-and-image">
      <Col className="pt-3 text-center" xs={6}>
        <h6>X: <span class="dbn-reference-canvas-demo-number">
            {xCoord}
          </span>
        </h6>

        <h6>Y: <span class="dbn-reference-canvas-demo-number">
            {yCoord}
          </span>
        </h6>
      </Col>

      <Col xs={6}>
        <canvas
          ref={canvasRef}
          height={121}
          width={121}
          onMouseMove={canvasMouseOver}
          onMouseLeave={canvasMouseOut}
          style={{
            position: 'relative',
            top:'-10px',
            left: '-10px',
            cursor: 'crosshair',
          }}
        />
      </Col>
    </Row>
  )
}

export default CanvasCoordinatesDemonstration
