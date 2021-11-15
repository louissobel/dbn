/* eslint import/no-anonymous-default-export: "off" */

import {keccak256} from "@ethersproject/keccak256"
import { BN } from 'ethereumjs-util'

import {
  initCanvas,
  varsFromSpec,
} from './helpers'

export default {
  name: 'sha3',

  initialSpec: [
    {value: "Number Abs X {", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "  Smaller? X 0 {", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "    Value (0 - X)", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "  }", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "  Value X", type: 'constant'},
    {value: "\n", type: 'constant'},
    {value: "}", type: 'constant'},
    {value: "\n", type: 'constant'},

    {value: "\n", type: 'constant'},

    {value: "Set S <Abs <SHA3", type: 'constant'},
    {value: '50', name: 'i', type: 'xcoord'},
    {value: ">>", type: 'constant', nospace: true},
    {value: "\n", type: 'constant'},

    {value: 'Repeat i 0 31 {', type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: '  Set X (3 + i*3)', type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: "  Line X 0 X (S % 101)", type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: "  Set S (S / 101)", type: 'constant'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
  ],

  draw(ctx, spec, tooltipItemName) {
    initCanvas(ctx)

    let [i] = varsFromSpec(['i'], spec)

    let u = new Uint8Array(32)
    u[31] = i
    let s = new BN(keccak256(u).slice(2), 16)
    let bit255 = new BN(1).shln(255)

    // Simulate u256 ABS if it is "negative" (not + 1)
    if (!bit255.and(s).eqn(0)) {
      s = s.notn(256).add(new BN(1))
    }


    for (let i = 0; i<32; i++) {
      let h = s.modn(101) + 1;
      let img = ctx.createImageData(1, h)
      for (var j = 0; j < h; j++) {
        img.data[j*4 + 3] = 255 // (alpha)
      }
      ctx.putImageData(img, 10 + 3 + i*3, 10 + 100 - (h - 1))

      s = s.divn(101)
    }

  }
}

