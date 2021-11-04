import {
  varsFromSpec,
  initCanvas,
  drawLine,
  drawPaper,
  getSpecItemForTooltip,
  drawTooltipGuide,
} from './helpers'

export default {
  name: 'pen',

  initialSpec: [
    {value: "Paper", type: 'constant'},
    {value: '65', type: 'color', name: 'paper'},
    {value: '\n', type: 'constant'},
    {value: "Pen", type: 'constant'},
    {value: '10', type: 'color', name: 'pen1'},
    {value: '\n', type: 'constant'},
    {value: "Line", type: 'constant'},
    {value: '10', name: 'x01', type: 'xcoord'},
    {value: '10', name: 'y01', type: 'ycoord'},
    {value: '90', name: 'x11', type: 'xcoord'},
    {value: '90', name: 'y11', type: 'ycoord'},
    {value: '\n', type: 'constant'},
    {value: "Line", type: 'constant'},
    {value: '20', name: 'x02', type: 'xcoord'},
    {value: '10', name: 'y02', type: 'ycoord'},
    {value: '90', name: 'x12', type: 'xcoord'},
    {value: '80', name: 'y12', type: 'ycoord'},
    {value: '\n', type: 'constant'},
    {value: "Pen", type: 'constant'},
    {value: '90', type: 'color', name: 'pen2'},
    {value: '\n', type: 'constant'},
    {value: "Line", type: 'constant'},
    {value: '0', name: 'x03', type: 'xcoord'},
    {value: '100', name: 'y03', type: 'ycoord'},
    {value: '100', name: 'x13', type: 'xcoord'},
    {value: '0', name: 'y13', type: 'ycoord'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [
      paper,
      pen1,
      x01,
      y01,
      x11,
      y11,
      x02,
      y02,
      x12,
      y12,
      pen2,
      x03,
      y03,
      x13,
      y13,
    ] = varsFromSpec([
      'paper',
      'pen1',
      'x01',
      'y01',
      'x11',
      'y11',
      'x02',
      'y02',
      'x12',
      'y12',
      'pen2',
      'x03',
      'y03',
      'x13',
      'y13',
    ], spec)

    initCanvas(ctx)

    drawPaper(ctx, paper)

    drawLine(ctx, pen1, x01, y01, x11, y11)
    drawLine(ctx, pen1, x02, y02, x12, y12)
    drawLine(ctx, pen2, x03, y03, x13, y13)

    let tooltipItem = getSpecItemForTooltip(spec, tooltipItemName)
    if (tooltipItem && (tooltipItem.type === 'xcoord' || tooltipItem.type === 'ycoord')) {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'y01': 'y11',
        'y11': 'y01',
        'x01': 'x11',
        'x11': 'x01',
        'y02': 'y12',
        'y12': 'y02',
        'x02': 'x12',
        'x12': 'x02',
        'y03': 'y13',
        'y13': 'y03',
        'x03': 'x13',
        'x13': 'x03',
      })
    }
  }
}
