import {
  varsFromSpec,
  initCanvas,
  dbnColorToByte,
  drawTooltipGuide,
} from './helpers'

export default {
  name: 'repeat',

  initialSpec: [
    {value: 'Repeat X', type: 'constant'},
    {value: '25', name: 'start', type: 'xcoord'},
    {value: '75', name: 'end', type: 'xcoord'},
    {value: '{', type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: '  Pen X', type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: "  Line", type: 'constant'},
    {value: 'X', type: 'constant'},
    {value: '0', name: 'y0', type: 'ycoord'},
    {value: 'X', type: 'constant'},
    {value: '100', name: 'y1', type: 'ycoord'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [start, end, y0, y1]  = varsFromSpec([
      'start',
      'end',
      'y0',
      'y1',
    ], spec)

    initCanvas(ctx)

    let height = Math.abs(y1 - y0) + 1
    let yTop = Math.max(y1, y0)

    for (let x = Math.min(start, end); x < Math.max(start, end) + 1; x++) {
      let img = ctx.createImageData(1, height)
      for (var i = 0; i<height; i++) {
        let c = dbnColorToByte(x)
        img.data[i*4 + 0] = c
        img.data[i*4 + 1] = c
        img.data[i*4 + 2] = c
        img.data[i*4 + 3] = 255 // (alpha channel)
      }
      ctx.putImageData(img, x+10, (100-yTop) + 10)
    }

    if (tooltipItemName) {
      drawTooltipGuide(ctx, spec, tooltipItemName, {
        'start': 'end',
        'end': 'start',
        'y0': 'y1',
        'y1': 'y0',
      })
    }
  }
}
