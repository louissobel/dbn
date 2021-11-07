const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')

import { task } from "hardhat/config";

task("deploy-helper", "Deploys the DBN helpers contracts")
  .addParam(
    "contractCode",
    "the file containing the bytecode of the helper",
  )
  .setAction(async ({ contractCode }) => {
    const hre = require("hardhat");

    const code = fs.readFileSync(contractCode)

    const codeLength = code.length;
    const deployHeader = Buffer.from([
      // push length
      0x61, ((codeLength & 0xFF00) >> 8), (codeLength & 0xFF),

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

    const fullBuffer = Buffer.concat([deployHeader, code])
    console.log(fullBuffer)


    const signer = (await hre.ethers.getSigners())[0]
    const abi = ["constructor()"];
    const factory = new hre.ethers.ContractFactory(
      abi,
      "0x" + fullBuffer.toString('hex'),
      signer,
    )
    const contract = await factory.deploy();
    console.log(contract.address);

    await contract.deployTransaction.wait();
    console.log("helpers deployed")

    console.log(contract.address.toLowerCase().slice(2))
    console.log(code.toString('hex'))
  });
