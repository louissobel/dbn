const fs = require('fs')
const util = require('util')

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
    const defaultOwner = (await hre.ethers.getSigners())[0].address

    // Deploy the DBNCoordinator contract
    // Deploy Base64?
    // Call DBNCoordinator "deploy" with passed drawing
    // Ask the coordinator to render that drawing for us

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = await DBNCoordinator.deploy(
      defaultOwner,
      "http://localhost:3000/dbnft/",
      "0x0000000000000000000000000000000000000000",
    );
    await coordinator.deployed();
    const coordinatorDeployReceipt = await coordinator.deployTransaction.wait()

    console.log("Coordinator deployed to: ", coordinator.address, `(Gas used: ${coordinatorDeployReceipt.gasUsed.toString()})`);

    // Open up minting
    await coordinator.openMinting()
    console.log("Opened up minting")

    const input = fs.readFileSync(file);

    const codeToDeploy = Buffer.concat([
      input,
    ])

    // stick on the deploy header
    // (todo: clearly need something more robuse than hand-coding it...)
    if (codeToDeploy.length > 0xffff) { throw new Error("hardcoding PUSH2, cannot handle this long code")}

    const deployHeader = Buffer.from([
      // push length
      0x61, ((codeToDeploy.length & 0xFF00) >> 8), (codeToDeploy.length & 0xFF),

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
    const mintInput = Buffer.concat([deployHeader, codeToDeploy])

    const mintTxn =  await coordinator.mint(mintInput, {
      value: hre.ethers.utils.parseEther('0.01', 'ethers'),
    })
    const mintTxnReceipt = await mintTxn.wait()

    const transferEvent = mintTxnReceipt.events.find((e: any) =>
      e.event === 'Transfer'
    )
    console.log("NFT created with id: ", transferEvent.args.tokenId._hex, `(Gas used: ${mintTxnReceipt.gasUsed.toString()})`)

    const deployEvent = mintTxnReceipt.events.find((e: any) =>
      e.event === 'DrawingDeployed'
    )
    console.log("Drawing Deployed to: ", deployEvent.args.addr)

    const tokenURI = await coordinator.tokenURI(transferEvent.args.tokenId)
    const parsed = JSON.parse(tokenURI.split('data:application/json,')[1])

    console.log("Got Token Metadata")
    console.log(util.inspect(parsed, {
      maxStringLength: 255,
      colors: true,
    }))


    // OK, find the image data
    if (parsed.image_data) {
      const filename = output + '.svg';
      console.log(` -> Writing image (raw SVG from image_data) to ${filename}`)
      fs.writeFileSync(filename, parsed.image_data)

    } else if (parsed.image) {
      const rawFilename = output + '.datauri'
      console.log(` -> Writing raw .image datauri to ${rawFilename}`)
      fs.writeFileSync(rawFilename, parsed.image)

      // just split at first comma
      const parts = parsed.image.split(',')
      const contentType = parts.shift();
      const data = parts.join(',')

      if (contentType === 'data:image/bmp;base64') {
        const filename = output + '.bmp'
        console.log(` -> Writing image (BMP from image) to ${filename}`)
        fs.writeFileSync(filename, Buffer.from(data, 'base64'))

      } else if (contentType === 'data:image/svg+xml') {
        const filename = output + '.svg'
        console.log(` -> Writing image (SVG from image) to ${filename}`)
        fs.writeFileSync(filename, data)
      } else {
        throw new Error('unknown content type')
      }
    } else {
      throw new Error('no image or image_data!')
    }

  });


