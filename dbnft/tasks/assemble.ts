const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')

import { task } from "hardhat/config";

task("assemble", "Assembles given file and evals with debugger attached")
  .addParam(
    "file",
    "The file containing ethers.js ASM",
  )
  .addParam(
    "output",
    "Where to write the file",
  )
  .setAction(async ({ file, output }) => {

    const data = fs.readFileSync(file, 'utf-8');
    const parsed = asm.parse(data);
    const assembled = await asm.assemble(parsed, {});
    fs.writeFileSync(output, Buffer.from(assembled.slice(2), 'hex'))
  });