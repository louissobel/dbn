import {assemble, parse} from "@ethersproject/asm";
import VM from '@ethereumjs/vm'
import { Block } from '@ethereumjs/block'

// eslint-disable-next-line import/no-webpack-loader-syntax
import harness from '!!raw-loader!../contracts/drawHarness.ethasm'

var evmAssemble = async function(data) {
	const full = harness + "\n\n\n" + ";".repeat(50) + data;
	const ast = parse(full)
	return await assemble(ast, {})
}

var evmInterpret = async function(bytecode, opts, onStep) {
  const vm = new VM({})

  if (onStep) {
    vm.on('step', onStep)
  }

  const block = Block.fromBlockData({
    header: {
      // TODO: make this user-configurable in the header?
      timestamp: Math.floor(Date.now() / 1000),
    }
  })

	const runOpts = {
    code: Buffer.from(bytecode.slice(2), 'hex'),
    block: block,
    gasLimit: opts.gasLimit,
    // no call data right now
    data: opts.data,
  }

  try {
    return await vm.runCode(runOpts)
  } finally {
    if (onStep) {
      vm.removeListener('step', onStep)
    }
  }
}

export {
	evmAssemble,
	evmInterpret,
}