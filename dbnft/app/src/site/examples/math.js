import {
  varsFromSpec,
  initCanvas,
  makeDBNColorPixel,
} from './helpers'

export default {
  name: 'math',

  initialSpec: [
    {value: 'Repeat X', type: 'constant'},
    {value: '0', name: 'start', type: 'xcoord'},
    {value: '100', name: 'end', type: 'xcoord'},
    {value: '{', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '  Set Xs (X -', type: 'constant'},
    {value: '50', name: 'xshift', type: 'xcoord'},
    {value: ')', type: 'constant', nospace: true},
    {value: '\n', type: 'constant'},

    {value: '  Set X2 (Xs * Xs)', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '  Set Y (X2 /', type: 'constant'},
    {value: '50', name: 'd', type: 'xcoord'},
    {value: '+', type: 'constant'},
    {value: '50', name: 'yshift', type: 'ycoord'},
    {value: ')', type: 'constant', nospace: true},
    {value: '\n', type: 'constant'},

    {value: '  Set [X Y]', type: 'constant'},
    {value: '100', type: 'color', name: 'pen'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let [start, end, xshift, d, yshift, pen] = varsFromSpec([
      'start',
      'end',
      'xshift',
      'd',
      'yshift',
      'pen'
    ], spec)

    initCanvas(ctx)

    const p = makeDBNColorPixel(ctx, pen)
    for (let x = Math.min(start, end); x < Math.max(start, end) + 1; x++) {
      let Xs = x - xshift;
      let X2 = Xs * Xs;

      let y;
      if (d === 0) {
        y = yshift // that's how divide-by-zero works in evm
      } else {
        y = Math.floor(X2/d) + yshift
      }

      if (x >= 0 && x <= 100 && y >= 0 && y <= 100) {
        ctx.putImageData(p, x + 10, (100-y)+10)
      }
    }
  }
}
