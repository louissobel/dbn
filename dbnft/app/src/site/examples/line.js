/* eslint import/no-anonymous-default-export: "off" */

import {
  varsFromSpec,
  initCanvas,
  drawLine,
  drawTooltipGuide,
} from './helpers'


export const line =  {
  name: 'line',

  initialSpec: [
    {value: "Line", type: 'constant'},
    {value: '0', name: 'x0', type: 'xcoord'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: '100', name: 'x1', type: 'xcoord'},
    {value: '100', name: 'y1', type: 'ycoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [x0, y0, x1, y1] = varsFromSpec(['x0', 'y0', 'x1', 'y1'], spec)

    initCanvas(ctx)
    drawLine(ctx, 100, x0, y0, x1, y1)

    if (tooltipItemName) {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'y0': 'y1',
        'y1': 'y0',
        'x0': 'x1',
        'x1': 'x0',
      })
    }
  }
}


export const commentedLine =  {
  name: 'commentedLine',

  initialSpec: [
    {value: "// Line is passed four parameters:", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "//  - x0: the x coordinate of the first point", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "//  - y0: the y coordinate of the first point", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "//  - x1: the x coordinate of the second point", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "//  - y1: the y coordinate of the second point", type: 'constant'},
    {value: "\n", type: 'constant'},


    {value: "Line", type: 'constant'},
    {value: '0', name: 'x0', type: 'xcoord'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: '100', name: 'x1', type: 'xcoord'},
    {value: '100', name: 'y1', type: 'ycoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [x0, y0, x1, y1] = varsFromSpec(['x0', 'y0', 'x1', 'y1'], spec)

    initCanvas(ctx)
    drawLine(ctx, 100, x0, y0, x1, y1)

    if (tooltipItemName) {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'y0': 'y1',
        'y1': 'y0',
        'x0': 'x1',
        'x1': 'x0',
      })
    }
  }
}


export const describedLine =  {
  name: 'describedLine',

  initialSpec: [
    {value: "//description: Line Example", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "Line", type: 'constant'},
    {value: '0', name: 'x0', type: 'xcoord'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: '100', name: 'x1', type: 'xcoord'},
    {value: '100', name: 'y1', type: 'ycoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [x0, y0, x1, y1] = varsFromSpec(['x0', 'y0', 'x1', 'y1'], spec)

    initCanvas(ctx)
    drawLine(ctx, 100, x0, y0, x1, y1)

    if (tooltipItemName) {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'y0': 'y1',
        'y1': 'y0',
        'x0': 'x1',
        'x1': 'x0',
      })
    }
  }
}
