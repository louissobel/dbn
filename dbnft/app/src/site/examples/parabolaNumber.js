/* eslint import/no-anonymous-default-export: "off" */

import {drawParabola} from './math'


export default  {
  name: 'parabolaNumber',

  initialSpec: [
    {value: "Number Parabola A H K X {", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "  Set X2 ((X-H)*(X-H))", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "  Value (X2/A + K)", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "}", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: 'Repeat X', type: 'constant'},
    {value: '0', name: 'start', type: 'xcoord'},
    {value: '100', name: 'end', type: 'xcoord'},
    {value: '{', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '  Set Y <Parabola', type: 'constant'},
    {value: '50', name: 'd', type: 'xcoord'},
    {value: '50', name: 'xshift', type: 'xcoord'},
    {value: '50', name: 'yshift', type: 'ycoord'},
    {value: 'X>', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '  Set [X Y]', type: 'constant'},
    {value: '100', type: 'color', name: 'pen'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
  ],

  draw(ctx, spec, tooltipItemName) {
    drawParabola(ctx, spec)
  }
}
