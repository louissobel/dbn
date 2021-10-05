const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')
import VM from '@ethereumjs/vm'
import InteractiveDebugger from './interactive_debugger'

import { task } from "hardhat/config";

task("assemble-and-debug", "Assembles given file and evals with debugger attached")
  .addParam(
    "file",
    "The file containing ethers.js ASM",
  )
  .addOptionalParam(
    "calldata",
    "Hexstring calldata",
  )
  .addFlag(
    "resultAsString",
    "Render the result as EVM ABI string",
  )
  .setAction(async (params) => {

    const { file } = params;

    const data = fs.readFileSync(file, 'utf-8');
    const parsed = asm.parse(data);
    const assembled = await asm.assemble(parsed, {});
    console.log("Code Length: ", assembled.length - 2);
    console.log("Code: ", assembled);

    const vm = new VM({
      interpreterDebugger: new InteractiveDebugger(),
    })

    const runOpts = {
      code: Buffer.from(assembled.slice(2), 'hex'),
      gasLimit: new BN(0xffffffff),
      data: params.calldata ? Buffer.from(params.calldata.slice(2), 'hex') : undefined,
    }
    const result = await vm.runCode(runOpts)

    if (result.exceptionError) {
      throw new Error("failure: " + result.exceptionError.error)
    }

    console.log("Gas Used :", result.gasUsed.toString(10))

    // Raw return value
    const raw = "0x" + result.returnValue.toString('hex')
    console.log("Raw Return: ", raw);

    if (params.resultAsString) {
      const coder = new ethers.utils.AbiCoder()
      console.log("ABI String: ", coder.decode(["string"], raw))
    }


  });