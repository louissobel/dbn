const fs = require('fs')
const asm = require("@ethersproject/asm");

import { Account, Address, BN } from 'ethereumjs-util'
const ethers = require('ethers')
import VM from '@ethereumjs/vm'
import { Block } from '@ethereumjs/block'
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
  .addOptionalParam(
    "fixedTimestamp",
    "use a fixed timestamp rather than Date.now"
  )
  .addOptionalParam(
    "loadContract",
    "a address:file pair to load as code"
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

    if (params.loadContract) {
      const [addressString, path] = params.loadContract.split(':')
      const code = fs.readFileSync(path)
      const address = new Address(Buffer.from(addressString.slice(2), 'hex'))
      const account = Account.fromAccountData({ nonce: 0, balance: 0 })

      await vm.stateManager.checkpoint()
      await vm.stateManager.putAccount(address, account)
      await vm.stateManager.putContractCode(address, code)
      await vm.stateManager.commit()
    }

    var codeBuffer = Buffer.from(assembled.slice(2), 'hex')

    let timestamp;
    if (params.fixedTimestamp) {
      timestamp = parseInt(params.fixedTimestamp)
    } else {
      timestamp = Math.floor(Date.now() / 1000)
    }

    const block = Block.fromBlockData({
      header: {
        timestamp: timestamp,
      }
    })

    const runOpts = {
      code: codeBuffer,
      block: block,
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