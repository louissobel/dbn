import {assemble, parse} from "@ethersproject/asm";
import VM from '@ethereumjs/vm'
import { Account, Address } from 'ethereumjs-util'
import { Block } from '@ethereumjs/block'

// eslint-disable-next-line import/no-webpack-loader-syntax
import inlineHarness from '!!raw-loader!../contracts/drawHarness.ethasm'

// eslint-disable-next-line import/no-webpack-loader-syntax
import helperHarness from '!!raw-loader!../contracts/helpersDrawHarness.ethasm'


var linkCode = function (assemblyCode, opts) {
  if (opts.useHelpers) {
    return helperHarness + "\n\n\n" + assemblyCode
  } else {
    return inlineHarness + "\n\n\n" + assemblyCode
  }
}

var evmAssemble = async function(assembly) {
	const ast = parse(assembly)
	return await assemble(ast, {})
}

var evmInterpret = async function(bytecode, opts, onStep) {
  const vm = new VM({})

  if (onStep) {
    vm.on('step', onStep)
  }

  if (opts.helper) {
    const helperAddress = new Address(Buffer.from(opts.helper.address, 'hex'))
    const helperCode = Buffer.from(opts.helper.code, 'hex')
    const helperAccount = Account.fromAccountData({ nonce: 0, balance: 0 })

    await vm.stateManager.checkpoint()
    await vm.stateManager.putAccount(helperAddress, helperAccount)
    await vm.stateManager.putContractCode(helperAddress, helperCode)
    await vm.stateManager.commit()
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
  linkCode,
}