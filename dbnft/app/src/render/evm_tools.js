import {assemble, parse} from "@ethersproject/asm";
import VM from '@ethereumjs/vm'
import { Account, Address } from 'ethereumjs-util'
import { Block } from '@ethereumjs/block'

// eslint-disable-next-line import/no-webpack-loader-syntax
import drawHarness from '!!raw-loader!../contracts/drawHarness.ethasm'

import inlineLinkArtifact from '../contracts/inlineLinkArtifact.json'
import helpersLinkArtifact from '../contracts/helpersLinkArtifact.json'


var parseLinkList = function (data) {
  const lines = data.split("\n", 1)
  const firstLine = lines[0]
  if (firstLine.startsWith(';link:')) {
    let splitLine = firstLine.split(':')
    let linkString = splitLine[1]
    if (linkString.length > 1) {
      return linkString.split(',')
    } else {
      return []
    }
  } else {
    return []
  }
}

var linkCode = function (assemblyCode, opts) {
  let linkArtifact;

  if (opts.useHelpers) {
    linkArtifact = helpersLinkArtifact;
  } else {
    linkArtifact = inlineLinkArtifact;
  }

  const seen = {}
  const linkQueue = [drawHarness, assemblyCode]
  const output = []

  while (linkQueue.length > 0) {
    let next = linkQueue.shift()
    output.push(next)
    let links = parseLinkList(next)
    for (let link of links) {
      let data = linkArtifact[link];
      if (!data) {
        throw new Error('no data for linked function ' + link)
      }

      if (!seen[link]) {
        seen[link] = true;
        linkQueue.push(data)
      }
    }
  }

  /*
   This is a hack... the drawing needs to be at the end (to avoid padding metadata)
   but it is nice for the algorithm to treat it like other input.
   So just splice it out and re-push it to the end.
  */
  output.splice(1, 1)
  output.push(assemblyCode)

  return output.join("\n\n")
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

  if (opts.codeAddress) {
    runOpts.address = new Address(Buffer.from(opts.codeAddress.slice(2), 'hex'))
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