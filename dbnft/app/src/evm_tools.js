import {assemble, parse} from "@ethersproject/asm";
import VM from '@ethereumjs/vm'
import { BN } from 'ethereumjs-util'


// eslint-disable-next-line import/no-webpack-loader-syntax
import harness from '!!raw-loader!./contracts/drawHarness.ethasm'

var evmAssemble = async function(data) {
	const full = harness + "\n\n\n" + ";".repeat(50) + data;
	const ast = parse(full)
	return await assemble(ast, {})
}

var initializeVM = function() {
  return 
}

var evmInterpret = async function(bytecode, opts, onStep) {
  const vm = new VM({})

  if (onStep) {
    vm.on('step', onStep)
  }


	const runOpts = {
    code: Buffer.from(bytecode.slice(2), 'hex'),
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

// takes and returns hex
var prependDeployHeader = function(bytecode) {
  const inputLength = (bytecode.length - 2) / 2 // -2 takes off '0x'

  // TODO: throw error if input length is bigger than 0xFFFF
  const deployHeader = Buffer.from([
    // push length
    0x61, ((inputLength & 0xFF00) >> 8), (inputLength & 0xFF),

    // dup length
    0x80,

    // push code offset (same as length of deploy header...)
    0x60, 12,

    // push 0
    0x60, 0,

    // copy code into memory
    0x39,

    // get another zero on
    0x60, 0,

    // stack is now [0|length
    // code to deploy is at 0
    // so we're good to return :)
    0xF3
  ])

  return '0x' + deployHeader.toString('hex') + bytecode.slice(2)
}

export {
  initializeVM,
	evmAssemble,
	evmInterpret,
  prependDeployHeader
}