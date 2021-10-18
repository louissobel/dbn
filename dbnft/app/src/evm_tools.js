import {assemble, parse} from "@ethersproject/asm";
import VM from '@ethereumjs/vm'
import { BN } from 'ethereumjs-util'


// eslint-disable-next-line import/no-webpack-loader-syntax
import harness from '!!raw-loader!./ethasm/drawHarness.ethasm'

var evmAssemble = async function(data) {
	const full = harness + "\n\n\n" + ";".repeat(50) + data;
	const ast = parse(full)
	return await assemble(ast, {})
}

var evmInterpret = async function(bytecode) {
	const vm = new VM({})

	const runOpts = {
      code: Buffer.from(bytecode.slice(2), 'hex'),
      gasLimit: new BN(0xffffffff),
      // no call data right now
      // data: "",
    }

    // TODO: do something interesting with each VM step?
    // vm.on('step', function(e) {
    // 	debugger;
    // })

    return await vm.runCode(runOpts)
}

export {
	evmAssemble,
	evmInterpret
}