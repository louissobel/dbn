import {
  varsFromSpec,
  initCanvas,
  drawLine,
  drawTooltipGuide,
} from './helpers'


export default {
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
