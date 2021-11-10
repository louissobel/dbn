/* eslint import/no-anonymous-default-export: "off" */

import {
  varsFromSpec,
  initCanvas,
  drawLine,
  drawTooltipGuide,
} from './helpers'


export default  {
  name: 'squareCommand',

  initialSpec: [
    {value: "Command Square X Y S {", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "  Line X Y (X+S) Y", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "  Line (X+S) Y (X+S) (Y+S)", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "  Line (X+S) (Y+S) X (Y+S)", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "  Line X (Y+S) X Y", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "}", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: 'Square', type: 'constant'},
    {value: '20', name: 'x0', type: 'xcoord'},
    {value: '20', name: 'y0', type: 'ycoord'},
    {value: '60', name: 's0', type: 'xcoord'},
    {value: "\n", type: 'constant'},

    {value: 'Square', type: 'constant'},
    {value: '30', name: 'x1', type: 'xcoord'},
    {value: '30', name: 'y1', type: 'ycoord'},
    {value: '40', name: 's1', type: 'xcoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [x0, y0, s0, x1, y1, s1] = varsFromSpec(['x0', 'y0', 's0', 'x1', 'y1', 's1'], spec)

    initCanvas(ctx)

    function square(x, y, s) {

      let xEnd = Math.min(x+s, 100)
      let yEnd = Math.min(y+s, 100)


      drawLine(ctx, 100, x, y, xEnd, y)

      if (x+s <= 100) {
        drawLine(ctx, 100, x+s, y, x+s, yEnd)
      }

      if (y+s <= 100) {
        drawLine(ctx, 100, xEnd, y+s, x, y+s)
      }

      drawLine(ctx, 100, x, yEnd , x, y)
    }

    square(x0, y0, s0)
    square(x1, y1, s1)
  }
}
