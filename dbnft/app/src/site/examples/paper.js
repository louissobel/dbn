/* eslint import/no-anonymous-default-export: "off" */

import {
  varsFromSpec,
  drawPaper,
} from './helpers'

export const paper = {
  name: 'paper',

  initialSpec: [
    {value: 'Paper', type: 'constant'},
    {value: '75', type: 'color', name: 'v'}
  ],

  draw(ctx, spec, tooltipItemName) {
    let [v] = varsFromSpec(['v'], spec)

    drawPaper(ctx, v)
  }
}


export const paperCoveringLine = {
  name: 'paperCoveringLine',

  initialSpec: [
    {value: "Line", type: 'constant'},
    {value: '0', name: 'x0', type: 'xcoord'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: '100', name: 'x1', type: 'xcoord'},
    {value: '100', name: 'y1', type: 'ycoord'},
    {value: "\n", type: 'constant'},

    {value: 'Paper', type: 'constant'},
    {value: '75', type: 'color', name: 'v'}
  ],

  draw(ctx, spec, tooltipItemName) {
    let [v] = varsFromSpec(['v'], spec)

    drawPaper(ctx, v)
  }
}
