const hre = require("hardhat");

import { BN } from 'ethereumjs-util'
import Common, { Chain, Hardfork } from '@ethereumjs/common'
import VM from '@ethereumjs/vm'
import InteractiveDebugger from './interactive_debugger'

async function main() {
  const vm = new VM({
    interpreterDebugger: new InteractiveDebugger(),
  })
  // 6a68656c6c6f20776f726c64600052600B6015f3
  // 7B 6a68656c6c6f20776f726c6460a81b602052600b60005260406000f3 6000 52 601C 600c f3
  // 7A 6468656c6c6f60d81b6040526005602052600160005260606000f3 6000 52 601B 6005 f3

  const result = await vm.runCode({
    code: Buffer.from(Buffer.from("6468656c6c6f60d81b6040526005602052602060005260606000f3", 'hex')),
    gasLimit: new BN(0xffff),
  })

  if (result.exceptionError) {
    throw new Error("failure: " + result.exceptionError.error)
  }

  console.log(result.returnValue.toString('hex'));
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
