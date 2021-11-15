/* eslint import/no-anonymous-default-export: "off" */

import {
  varsFromSpec,
  initCanvas,
  drawPaper,
  dbnColorToByte,
  drawTooltipGuide,
} from './helpers'

export default {
  name: 'field',

  initialSpec: [
    {value: 'Paper', type: 'constant'},
    {value: '75', name: 'paper', type: 'color'},
    {value: '\n', type: 'constant'},
    {value: 'Field', type: 'constant'},
    {value: '25', name: 'x0', type: 'xcoord'},
    {value: '25', name: 'y0', type: 'ycoord'},
    {value: '75', name: 'x1', type: 'xcoord'},
    {value: '75', name: 'y1', type: 'ycoord'},
    {value: '20', name: 'color', type: 'color'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [paper, x0, y0, x1, y1, color]  = varsFromSpec([
      'paper',
      'x0',
      'y0',
      'x1',
      'y1',
      'color',
    ], spec)

    initCanvas(ctx)
    drawPaper(ctx, paper)

    let height = Math.abs(y1 - y0) + 1
    let yTop = Math.max(y1, y0)

    let c = dbnColorToByte(color)

    for (let x = Math.min(x0, x1); x < Math.max(x0, x1) + 1; x++) {
      let img = ctx.createImageData(1, height)
      for (var i = 0; i<height; i++) {
        img.data[i*4 + 0] = c
        img.data[i*4 + 1] = c
        img.data[i*4 + 2] = c
        img.data[i*4 + 3] = 255 // (alpha channel)
      }
      ctx.putImageData(img, x+10, (100-yTop) + 10)
    }

    if (tooltipItemName && ['x0', 'x1', 'y0', 'y1'].includes(tooltipItemName)) {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'x0': 'x1',
        'x1': 'x0',
        'y0': 'y1',
        'y1': 'y0',
      })
    }
  }
}