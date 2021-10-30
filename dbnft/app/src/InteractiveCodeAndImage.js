import React, {useState, useEffect, useRef} from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import UIEditableCodeMirror from './UIEditableCodeMirror'


// RGB for the "guidebar" to appear showing what's moving in Line
const GUIDEBAR_COLOR = [0x1b, 0x1b, 0xac]

function InteractiveCodeAndImage({ func, initialSpec }) {
  const canvasRef = useRef()
  const [spec, setSpec] = useState(initialSpec)
  const [tooltipItemName, setTooltipItemName] = useState(null)

  var fn;
  if (func === 'line') {
    fn = drawLine;
  } else if (func === 'paper') {
    fn = drawPaper;
  } else {
    throw new Error('unknown func: ' + fn)
  }

  useEffect(() => {
    fn(spec);
  }, [spec, tooltipItemName])


  function getSpecItemForTooltip() {
    if (tooltipItemName === null) {
      return null
    } else {
      return spec.find((i) => {
        return i.name === tooltipItemName
      })
    }
  }

  function drawLine(spec) {
    let [x0, y0, x1, y1] = spec.slice(1).map((i) => parseInt(i.value))

    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d')

    ctx.imageSmoothingEnabled = false;
    ctx.fillStyle = "white";
    ctx.clearRect(0, 0, 121, 121)
    ctx.fillRect(10, 10, 101, 101);

    if (tooltipItemName) {
      let guidePixel = ctx.createImageData(1, 1);
      guidePixel.data[0] = GUIDEBAR_COLOR[0]
      guidePixel.data[1] = GUIDEBAR_COLOR[1]
      guidePixel.data[2] = GUIDEBAR_COLOR[2]
      guidePixel.data[3] = 255;
      let specItem = getSpecItemForTooltip()
      let value = parseInt(specItem.value)

      for (let i = 0; i<121;i++) {
        if (specItem.type === 'ycoord') {
          let nudge = 1
          if (specItem.name === 'y1' && value > y0) {
            nudge = -1
          }
          if (specItem.name === 'y0' && value > y1) {
            nudge = -1
          }
          ctx.putImageData(guidePixel, i, 10 + 100 - value + nudge)
        } else {
          let nudge = -1
          if (specItem.name === 'x1' && value > x0) {
            nudge = 1
          }
          if (specItem.name === 'x0' && value > x1) {
            nudge = 1
          }
          ctx.putImageData(guidePixel, 10 + value + nudge, i)
        }
      }
    }

    const blackPixel = ctx.createImageData(1, 1);
    blackPixel.data[3] = 255;


    // bresenham to get it looking pixelly
    // http://stackoverflow.com/questions/2734714/modifying-bresenhams-line-algorithm
    let steep = Math.abs(y1 - y0) > Math.abs(x1 - x0)
    if (steep) {
      let t = x0
      x0 = y0
      y0 = t

      t = x1
      x1 = y1
      y1 = t
    }
    if (x0 > x1) {
      let t = x0
      x0 = x1
      x1 = t

      t = y0
      y0 = y1
      y1 = t
    }

    let ystep;
    if (y0 < y1) {
      ystep = 1
    } else {
      ystep = -1
    }

    let deltax = x1 - x0
    let deltay = Math.abs(y1 - y0)
    let error = -1 * (Math.floor(deltax/2))
    let y = y0

    for (let x = x0; x<x1+1; x++) {
      if (steep) {
        ctx.putImageData(blackPixel, y + 10, 10 + 100 - x)
      } else {
        ctx.putImageData(blackPixel, x + 10, 10 + 100 - y)
      }

      error = error + deltay
      if (error > 0) {
        y = y + ystep
        error = error - deltax
      }
    }
  }

  function drawPaper(spec) {
    let v = parseInt(spec[1].value)

    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d')

    let color = 255 * (1 - v / 100.0)
    ctx.fillStyle = `rgb(${color}, ${color}, ${color})`
    ctx.fillRect(10, 10, 101, 101)
  }


  return (

    <Row className="dbn-reference-code-and-image">
      <Col xs={6}>
        <UIEditableCodeMirror
          initialSpec={initialSpec}
          onChange={setSpec}
          onVisibleTooltipChange={setTooltipItemName}
        />
      </Col>

      <Col xs={6}>
        <canvas
          ref={canvasRef}
          height={121}
          width={121}
          style={{
            position: 'relative',
            top:'-10px',
            left: '-10px',
          }}
        />
      </Col>
    </Row>
  )
}

export default InteractiveCodeAndImage
