import {
  varsFromSpec,
  drawPaper,
  drawLine,
  dbnColorToByte,
  drawTooltipGuide,
  makeDBNColorPixel,
} from './helpers'

export default {
  name: 'dots',


  /*
  Paper 10
Set R 50
Repeat X 20 80 {
  Set [X R] X
}
Set X [0 R]
Line X 0 X 100
*/
  initialSpec: [
    {value: 'Paper', type: 'constant'},
    {value: '10', type: 'color', name: 'paper'},
    {value: '\n', type: 'constant'},

    {value: "Set R", type: 'constant'},
    {value: "50", type: 'ycoord', name: 'reference'},
    {value: '\n', type: 'constant'},

    {value: 'Repeat X', type: 'constant'},
    {value: '20', name: 'start', type: 'xcoord'},
    {value: '80', name: 'end', type: 'xcoord'},
    {value: '{', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '  Set [X R] X', type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: 'Set dotAlongR [', type: 'constant', nudgeEndIn: true},
    {value: '50', type: 'xcoord', name: 'xR', nospace: true},
    {value: 'R]', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: 'Set X dotAlongR', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: "Line", type: 'constant'},
    {value: 'X', type: 'constant'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: 'X', type: 'constant'},
    {value: '100', name: 'y1', type: 'ycoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [paper, reference, start, end, xR, y0, y1]  = varsFromSpec([
      'paper',
      'reference',
      'start',
      'end',
      'xR',
      'y0',
      'y1',
    ], spec)


    drawPaper(ctx, paper)

    let xE = paper;

    for (let x = Math.min(start, end); x < Math.max(start, end) + 1; x++) {
      let p = makeDBNColorPixel(ctx, x)
      ctx.putImageData(p, x+10, (100-reference) + 10)

      if (x === xR) {
        xE = xR
      }
    }

    drawLine(ctx, 100, xE, y0, xE, y1)
  }
}
