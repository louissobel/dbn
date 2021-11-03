import React, {useState, useEffect, useRef} from 'react';

import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import UIEditableCodeMirror from './UIEditableCodeMirror'


// RGB for the "guidebar" to appear showing what's moving in Line
const GUIDEBAR_COLOR = [0x1b, 0x1b, 0xac]

function varsFromSpec(vars, spec) {
  return vars.map((v) => {
    let item = spec.find((i) => {
      return i.name === v;
    })
    if (!item) {
      throw new Error(`unknown var ${v} in spec`)
    }

    return parseInt(item.value)
  })
}

function initCanvas(ctx) {
  ctx.fillStyle = "white";
  ctx.clearRect(0, 0, 121, 121)
  ctx.fillRect(10, 10, 101, 101);
}

function dbnColorToByte(dbnColor) {
  return 255 * (1 - dbnColor / 100.0);
}

function makeDBNColorPixel(ctx, dbnColor) {
  let byteColor = dbnColorToByte(dbnColor)
  let p = ctx.createImageData(1, 1);
  p.data[0] = byteColor;
  p.data[1] = byteColor;
  p.data[2] = byteColor;
  p.data[3] = 255;
  return p
}

function dbnColorToRGBString(dbnColor) {
    let byteColor = dbnColorToByte(dbnColor)
    return `rgb(${byteColor}, ${byteColor}, ${byteColor})`
}

function makeGuidePixel(ctx) {
  let p = ctx.createImageData(1, 1);
  p.data[0] = GUIDEBAR_COLOR[0]
  p.data[1] = GUIDEBAR_COLOR[1]
  p.data[2] = GUIDEBAR_COLOR[2]
  p.data[3] = 255;
  return p
}

function drawPaper(ctx, dbnColor) {
  ctx.fillStyle = dbnColorToRGBString(dbnColor)
  ctx.fillRect(10, 10, 101, 101)
}

function drawLine(ctx, dbnColor, x0, y0, x1, y1) {
  let p = makeDBNColorPixel(ctx, dbnColor);

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
      ctx.putImageData(p, y + 10, 10 + 100 - x)
    } else {
      ctx.putImageData(p, x + 10, 10 + 100 - y)
    }

    error = error + deltay
    if (error > 0) {
      y = y + ystep
      error = error - deltax
    }
  }
}

function drawHorizontalGuideline(ctx, value) {
  let guidePixel = makeGuidePixel(ctx);
  for (let x = 0; x<121;x++) {
    ctx.putImageData(guidePixel, x, 10 + 100 - value)
  }
}

function drawVerticalGuideline(ctx, value) {
  let guidePixel = makeGuidePixel(ctx);
  for (let y = 0; y<121;y++) {
    ctx.putImageData(guidePixel, 10 + value, y)
  }
}

function InteractiveCodeAndImage({ exampleFunc, initialSpec, noheaders }) {
  const canvasRef = useRef()
  const [spec, setSpec] = useState(initialSpec)
  const [tooltipItemName, setTooltipItemName] = useState(null)

  let fn = {
    'blank': blankExample,
    'line': lineExample,
    'paper': paperExample,
    'pen': penExample,
    'variable': variableExample,
    'repeat': repeatExample,
    'math': mathExample,
  }[exampleFunc]
  if (!fn) {
    throw new Error('unknown exampleFunc: ' + exampleFunc)
  }

  useEffect(() => {
    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d')

    fn(ctx);
  }, [fn, spec, tooltipItemName])


  function getSpecItemForTooltip() {
    if (tooltipItemName === null) {
      return null
    } else {
      return spec.find((i) => {
        return i.name === tooltipItemName
      })
    }
  }

  function drawTooltipGuide(ctx, nudgeMapping) {
    let specItem = getSpecItemForTooltip();
    let value = parseInt(specItem.value);

    let nudge = -1;
    let otherName = nudgeMapping[specItem.name]
    if (otherName) {
      let [other] = varsFromSpec([otherName], spec)
      if (value > other) {
        nudge = 1
      }
    }

    if (specItem.type === 'ycoord') {
      drawHorizontalGuideline(ctx, value + nudge)
    } else if (specItem.type === 'xcoord') {
      drawVerticalGuideline(ctx, value + nudge)
    } else {
      throw new Error('only know guides for y or x coords')
    }

  }

  function blankExample(ctx) {
    initCanvas(ctx)
  }

  function lineExample(ctx) {
    let [x0, y0, x1, y1] = varsFromSpec(['x0', 'y0', 'x1', 'y1'], spec)

    initCanvas(ctx)
    drawLine(ctx, 100, x0, y0, x1, y1)

    if (tooltipItemName) {
      drawTooltipGuide(ctx, {
        'y0': 'y1',
        'y1': 'y0',
        'x0': 'x1',
        'x1': 'x0',
      })
    }
  }

  function paperExample(ctx) {
    let [v] = varsFromSpec(['v'], spec)

    drawPaper(ctx, v)
  }

  function penExample(ctx) {
    let [
      paper,
      pen1,
      x01,
      y01,
      x11,
      y11,
      x02,
      y02,
      x12,
      y12,
      pen2,
      x03,
      y03,
      x13,
      y13,
    ] = varsFromSpec([
      'paper',
      'pen1',
      'x01',
      'y01',
      'x11',
      'y11',
      'x02',
      'y02',
      'x12',
      'y12',
      'pen2',
      'x03',
      'y03',
      'x13',
      'y13',
    ], spec)

    initCanvas(ctx)

    drawPaper(ctx, paper)

    drawLine(ctx, pen1, x01, y01, x11, y11)
    drawLine(ctx, pen1, x02, y02, x12, y12)
    drawLine(ctx, pen2, x03, y03, x13, y13)

    let tooltipItem = getSpecItemForTooltip()
    if (tooltipItem && (tooltipItem.type === 'xcoord' || tooltipItem.type === 'ycoord')) {
      drawTooltipGuide(ctx, {
        'y01': 'y11',
        'y11': 'y01',
        'x01': 'x11',
        'x11': 'x01',
        'y02': 'y12',
        'y12': 'y02',
        'x02': 'x12',
        'x12': 'x02',
        'y03': 'y13',
        'y13': 'y03',
        'x03': 'x13',
        'x13': 'x03',
      })
    }
  }

  function variableExample(ctx) {
    let [xval, y0, y1] = varsFromSpec(['xval', 'y0', 'y1'], spec)

    initCanvas(ctx)
    drawLine(ctx, 100, xval, y0, xval, y1)

    let tooltipItem = getSpecItemForTooltip()
    if (tooltipItem && tooltipItem.type === 'ycoord') {
      drawTooltipGuide(ctx, {
        'y1': 'y0',
        'y0': 'y1',
      })
    }
  }

  function repeatExample(ctx) {
    let [start, end, y0, y1]  = varsFromSpec([
      'start',
      'end',
      'y0',
      'y1',
    ], spec)

    initCanvas(ctx)
    ctx.imageSmoothingEnabled = false

    let height = Math.abs(y1 - y0) + 1
    let yTop = Math.max(y1, y0)

    for (let x = Math.min(start, end); x < Math.max(start, end) + 1; x++) {
      let img = ctx.createImageData(1, height)
      for (var i = 0; i<height; i++) {
        let c = dbnColorToByte(x)
        img.data[i*4 + 0] = c
        img.data[i*4 + 1] = c
        img.data[i*4 + 2] = c
        img.data[i*4 + 3] = 255 // (alpha channel)
      }
      ctx.putImageData(img, x+10, (100-yTop) + 10)
    }

    if (tooltipItemName) {
      drawTooltipGuide(ctx, {
        'start': 'end',
        'end': 'start',
        'y0': 'y1',
        'y1': 'y0',
      })
    }
  }

  function mathExample(ctx) {
    let [start, end, xshift, d, yshift, pen] = varsFromSpec([
      'start',
      'end',
      'xshift',
      'd',
      'yshift',
      'pen'
    ], spec)

    initCanvas(ctx)

    const p = makeDBNColorPixel(ctx, pen)
    for (let x = Math.min(start, end); x < Math.max(start, end) + 1; x++) {
      let Xs = x - xshift;
      let X2 = Xs * Xs;

      let y;
      if (d === 0) {
        y = yshift // that's how divide-by-zero works in evm
      } else {
        y = Math.floor(X2/d) + yshift
      }

      if (x >= 0 && x <= 100 && y >= 0 && y <= 100) {
        ctx.putImageData(p, x + 10, (100-y)+10)
      }
    }
  }

  return (

    <Row className="dbn-reference-code-and-image">
      <Col xs={7}>
        {!noheaders && <h6>Input:</h6>}
        <UIEditableCodeMirror
          initialSpec={initialSpec}
          onChange={setSpec}
          onVisibleTooltipChange={setTooltipItemName}
        />

      </Col>

      <Col xs={5}>
        {!noheaders && <h6>Output:</h6>}
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
