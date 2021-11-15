/* eslint import/no-anonymous-default-export: "off" */

import {
  drawPaper,
  drawLine,
  initCanvas,
} from './helpers'

export default {
  name: 'time',

  initialSpec: [
    {value: "Paper <Time 3>", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "Set H <Time 2>", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "Set X (<Time 1> * 4)", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "Pen 60", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: 'Line X 0 X H', type: 'constant'},
  ],

  draw(ctx, spec, tooltipItemName) {
    let now = Math.floor(Date.now() / 1000)

    let s = now % 60;
    let m = Math.floor(now / 60) % 60
    let h = Math.floor(now / (60 * 60)) % 24
    let x = h * 4

    initCanvas(ctx)
    drawPaper(ctx, s)
    drawLine(ctx, 60, x, 0, x, m)
  }
}
