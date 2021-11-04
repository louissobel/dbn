
// RGB for the "guidebar" to appear showing what's moving in Line
const GUIDEBAR_COLOR = [0x1b, 0x1b, 0xac]

export function initCanvas(ctx) {
  ctx.fillStyle = "white";
  ctx.clearRect(0, 0, 121, 121)
  ctx.fillRect(10, 10, 101, 101);
}

export function dbnColorToByte(dbnColor) {
  return 255 * (1 - dbnColor / 100.0);
}

export function makeDBNColorPixel(ctx, dbnColor) {
  let byteColor = dbnColorToByte(dbnColor)
  let p = ctx.createImageData(1, 1);
  p.data[0] = byteColor;
  p.data[1] = byteColor;
  p.data[2] = byteColor;
  p.data[3] = 255;
  return p
}

export function dbnColorToRGBString(dbnColor) {
    let byteColor = dbnColorToByte(dbnColor)
    return `rgb(${byteColor}, ${byteColor}, ${byteColor})`
}

export function makeGuidePixel(ctx) {
  let p = ctx.createImageData(1, 1);
  p.data[0] = GUIDEBAR_COLOR[0]
  p.data[1] = GUIDEBAR_COLOR[1]
  p.data[2] = GUIDEBAR_COLOR[2]
  p.data[3] = 255;
  return p
}

export function drawPaper(ctx, dbnColor) {
  ctx.fillStyle = dbnColorToRGBString(dbnColor)
  ctx.fillRect(10, 10, 101, 101)
}

export function drawLine(ctx, dbnColor, x0, y0, x1, y1) {
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

export function drawHorizontalGuideline(ctx, value) {
  let guidePixel = makeGuidePixel(ctx);
  for (let x = 0; x<121;x++) {
    ctx.putImageData(guidePixel, x, 10 + 100 - value)
  }
}

export function drawVerticalGuideline(ctx, value) {
  let guidePixel = makeGuidePixel(ctx);
  for (let y = 0; y<121;y++) {
    ctx.putImageData(guidePixel, 10 + value, y)
  }
}

export function drawTooltipGuide(ctx, spec, tooltipItemName, nudgeMapping) {
  let specItem = getSpecItemForTooltip(spec, tooltipItemName);
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

export function varsFromSpec(vars, spec) {
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


export function getSpecItemForTooltip(spec, tooltipItemName) {
  if (tooltipItemName === null) {
    return null
  } else {
    return spec.find((i) => {
      return i.name === tooltipItemName
    })
  }
}
