const fs = require('fs')
const asm = require("@ethersproject/asm");

import { task } from "hardhat/config";


task("end-to-end-render-drawing", "Assembles given file and evals with debugger attached")
  .addParam(
    "file",
    "The file containing compiled drawing",
  )
  .addParam(
    "output",
    "Where to write the file",
  )
  .setAction(async ({ file, output }) => {
    const hre = require("hardhat");
    await hre.run("compile");

    // Deploy the DBNCoordinator contract
    // Deploy Base64?
    // Call DBNCoordinator "deploy" with passed drawing
    // Ask the coordinator to render that drawing for us

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = await DBNCoordinator.deploy();
    await coordinator.deployed();
    const coordinatorDeployReceipt = await coordinator.deployTransaction.wait()

    console.log("Coordinator deployed to: ", coordinator.address, `(Gas used: ${coordinatorDeployReceipt.gasUsed.toString()})`);

    const input = fs.readFileSync(file);

    // stick on the deploy header
    // (todo: clearly need something more robuse than hand-coding it...)
    if (input.length > 0xffff) { throw new Error("hardcoding PUSH2, cannot handle this long code")}


    const deployHeader = Buffer.from([
      // push length
      0x61, ((input.length & 0xFF00) >> 8), (input.length & 0xFF),

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
    const deployTxn =  await coordinator.deploy(Buffer.concat([deployHeader, input]))
    const deployTxnReceipt = await deployTxn.wait()

    const transferEvent = deployTxnReceipt.events.find((e: any) =>
      e.event === 'Transfer'
    )
    console.log("NFT created with id: ", transferEvent.args.tokenId._hex, `(Gas used: ${deployTxnReceipt.gasUsed.toString()})`)

    const deployEvent = deployTxnReceipt.events.find((e: any) =>
      e.event === 'DrawingDeployed'
    )
    console.log("Drawing Deployed to: ", deployEvent.args.addr)

    const tokenURI = await coordinator.tokenURI(transferEvent.args.tokenId)
    const parsed = JSON.parse(tokenURI.split('data:application/json,')[1])

    console.log("Got Token Metadata")
    console.log(" -> Name: ", parsed.name)
    console.log(" -> Description: ", parsed.description)
    console.log(" -> External URL: ", parsed.external_url)
    console.log(" -> Attributes: ", parsed.attributes)

    const imageData = Buffer.from(parsed.image.split('data:image/bmp;base64,')[1], 'base64')
    console.log(` -> Writing image to ${output}`)
    fs.writeFileSync(output, imageData)
  });




