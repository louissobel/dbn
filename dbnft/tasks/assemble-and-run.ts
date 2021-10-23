const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')
import VM from '@ethereumjs/vm'
import InteractiveDebugger from './interactive_debugger'

import { task } from "hardhat/config";

task("assemble-and-run", "Assembles given file and evals with debugger attached")
  .addParam(
    "file",
    "The file containing ethers.js ASM",
  )
  .addOptionalParam(
    "calldata",
    "Hexstring calldata",
  )
  .addOptionalParam(
    "outputFile",
    "write bytes",
  )
  .addFlag(
    "resultAsString",
    "Render the result as EVM ABI string",
  )
  .addFlag(
    "rawReturn",
    "Print the raw return value",
  )
  .addFlag(
    "debug",
    "enable the debugger",
  )
  .setAction(async (params) => {

    const { file, debug } = params;

    const data = fs.readFileSync(file, 'utf-8');
    const parsed = asm.parse(data);
    const assembled = await asm.assemble(parsed, {});
    console.log("Code Length: ", (assembled.length - 2)/2);
    // console.log("Code: ", assembled);


    var vmOpts = {}
    if (debug) {
      vmOpts = {
        interpreterDebugger: new InteractiveDebugger(),
      }
    }
    const vm = new VM(vmOpts)

    var codeBuffer = Buffer.from(assembled.slice(2), 'hex')

    const runOpts = {
      code: codeBuffer,
      gasLimit: new BN(0xffffffff),
      data: params.calldata ? Buffer.from(params.calldata.slice(2), 'hex') : undefined,
    }
    const result = await vm.runCode(runOpts)

    if (result.exceptionError) {
      if (result.exceptionError.error === 'revert') {
        console.log("!!!!!!!!!Revert!!!!!!!")
      } else {
        throw new Error("failure: " + result.exceptionError.error)
      }
    }

    console.log("Gas Used :", result.gasUsed.toString(10))

    // Raw return value
    const raw = "0x" + result.returnValue.toString('hex')
    // console.log("Raw Return: ", raw);

    const coder = new ethers.utils.AbiCoder()
    if (params.resultAsString) {
      console.log("ABI String: ", coder.decode(["string"], raw))
    } else if (params.rawReturn) {
      console.log("Raw Return: ", raw)
    }


    if (params.outputFile) {
      fs.writeFileSync(
        params.outputFile,
        Buffer.from(raw.slice(2), 'hex')
      )
    }

  });