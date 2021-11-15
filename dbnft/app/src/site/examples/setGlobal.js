/* eslint import/no-anonymous-default-export: "off" */

import {
  drawPaper,
  drawLine,
  initCanvas,
  varsFromSpec,
} from './helpers'


function setGlobalSpec(includeGlobal) {
  return [
    {value: "Set Y", type: 'constant'},
    {value: "50", name: 'y0', type: 'ycoord'},
    {value: "\n", type: 'constant'},

    {value: "Number NextY {", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "  Set my Y", type: 'constant'},
    {value: "\n", type: 'constant'},

    {
      value: includeGlobal ? "  Set Global Y (my + 1)" : "  Set Y (my + 1)",
      type: 'constant',
    },
    {value: "\n", type: 'constant'},

    {value: "  Value my", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "}", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: 'Repeat X', type: 'constant'},
    {value: '0', name: 'start', type: 'xcoord'},
    {value: '100', name: 'end', type: 'xcoord'},
    {value: '{', type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: '  Set [X <NextY>]', type: 'constant'},
    {value: '100', name: 'pen', type: 'color'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
  ]
}

export const setGlobalNotGlobal =  {
  name: 'setGlobalNotGlobal',

  initialSpec: setGlobalSpec(false),

  draw(ctx, spec, tooltipItemName) {
    initCanvas(ctx)

    let [y0, start, end, pen]  = varsFromSpec([
      'y0',
      'start',
      'end',
      'pen',
    ], spec)

    drawLine(ctx, pen, start, y0, end, y0)
  }
}

export const setGlobalGlobal =  {
  name: 'setGlobalGlobal',

  initialSpec: setGlobalSpec(true),

  draw(ctx, spec, tooltipItemName) {
    initCanvas(ctx)

    let [y0, start, end, pen]  = varsFromSpec([
      'y0',
      'start',
      'end',
      'pen',
    ], spec)

    drawLine(ctx, pen, start, y0, end, y0 + Math.abs(start - end))
  }
}
