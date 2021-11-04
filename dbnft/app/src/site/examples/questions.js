import {
  varsFromSpec,
  dbnColorToByte,
  initCanvas,
} from './helpers'


function makeInitialSpec(question1, question2) {
  return [
    {value: 'Set C', type: 'constant'},
    {value: '50', name: 'cutoff', type: 'xcoord'},
    {value: '\n', type: 'constant'},

    {value: 'Repeat X', type: 'constant'},
    {value: '10', name: 'start', type: 'xcoord'},
    {value: '90', name: 'end', type: 'xcoord'},
    {value: '{', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: `  ${question1} X C {`, type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '    Pen', type: 'constant'},
    {value: '75', type: 'color', name: 'pen1'},
    {value: '\n', type: 'constant'},
    {value: '  }', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: `  ${question2} X C {`, type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: '    Pen', type: 'constant'},
    {value: '25', type: 'color', name: 'pen2'},
    {value: '\n', type: 'constant'},
    {value: '  }', type: 'constant'},
    {value: '\n', type: 'constant'},

    {value: "  Line", type: 'constant'},
    {value: 'X', type: 'constant'},
    {value: '10', name: 'y0', type: 'ycoord'},
    {value: 'X', type: 'constant'},
    {value: '90', name: 'y1', type: 'ycoord'},
    {value: '\n', type: 'constant'},
    {value: '}', type: 'constant'},
  ]
}

function makeDrawFunction(compareForPen1) {
  return function(ctx, spec, tooltipItemName) {
    let [cutoff, start, end, pen1, pen2, y0, y1] = varsFromSpec([
      'cutoff',
      'start',
      'end',
      'pen1',
      'pen2',
      'y0',
      'y1',
    ], spec)

    initCanvas(ctx)

    let height = Math.abs(y1 - y0) + 1
    let yTop = Math.max(y1, y0)

    for (let x = Math.min(start, end); x < Math.max(start, end) + 1; x++) {
      let img = ctx.createImageData(1, height)
      for (var i = 0; i<height; i++) {
        let pen = pen2;
        if (compareForPen1(x, cutoff)) {
          pen = pen1
        }

        let c = dbnColorToByte(pen)
        img.data[i*4 + 0] = c
        img.data[i*4 + 1] = c
        img.data[i*4 + 2] = c
        img.data[i*4 + 3] = 255 // (alpha channel)
      }
      ctx.putImageData(img, x+10, (100-yTop) + 10)
    }

    console.log(cutoff, start, end, pen1, pen2, y0, y1)
  }
}

export const questionSame = {
  name: 'Same? / NotSame?',

  initialSpec: makeInitialSpec('Same?', 'NotSame?'),

  draw: makeDrawFunction((a, b) => a === b)
}

export const questionSmaller = {
  name: 'Smaller? / NotSmaller?',

  initialSpec: makeInitialSpec('Smaller?', 'NotSmaller?'),

  draw: makeDrawFunction((a, b) => a < b)
}
