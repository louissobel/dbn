import {
  varsFromSpec,
  drawPaper,
} from './helpers'

export default {
  name: 'paper',

  initialSpec: [
    {value: 'Paper', type: 'constant'},
    {value: '100', type: 'color', name: 'v'}
  ],

  draw(ctx, spec, tooltipItemName) {
    let [v] = varsFromSpec(['v'], spec)

    drawPaper(ctx, v)
  }
}
