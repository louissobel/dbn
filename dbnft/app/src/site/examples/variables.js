/* eslint import/no-anonymous-default-export: "off" */

import {
  varsFromSpec,
  initCanvas,
  drawLine,
  getSpecItemForTooltip,
  drawTooltipGuide
} from './helpers'

export default {
  name: 'variables',

  initialSpec: [
    {value: "Set X", type: 'constant'},
    {value: "50", type: 'xcoord', name: 'xval'},
    {value: '\n', type: 'constant'},
    {value: "Line", type: 'constant'},
    {value: 'X', type: 'constant'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: 'X', type: 'constant'},
    {value: '100', name: 'y1', type: 'ycoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [xval, y0, y1] = varsFromSpec(['xval', 'y0', 'y1'], spec)

    initCanvas(ctx)
    drawLine(ctx, 100, xval, y0, xval, y1)

    let tooltipItem = getSpecItemForTooltip(spec, tooltipItemName)
    if (tooltipItem && tooltipItem.type === 'ycoord') {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'y1': 'y0',
        'y0': 'y1',
      })
    }
  }
}
