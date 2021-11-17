const fs = require('fs')
const util = require('util')

const ethers = require('ethers')

import { task } from "hardhat/config";

task("get-token-uri", "Fetches / pretty prints token URI")
  .addParam(
    "coordinator",
    "Address of coordinator contract (in hex)",
  )
  .addParam(
    "tokenId",
    "tokenID (in decimal)"
  )
  .addOptionalParam(
    "saveImageDataTo",
    "a file path to save the image data to"
  )
  .setAction(async (params) => {
    const hre = require("hardhat");

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = DBNCoordinator.attach(params.coordinator)
    const tokenURI = await coordinator.tokenURI(params.tokenId)

    const parsed = JSON.parse(tokenURI.split('data:application/json,')[1])
    const output = util.inspect(parsed, {
      maxStringLength: 255,
      colors: true,
    })
    console.log(output)

    if (params.saveImageDataTo) {
      // OK, find the image data
      // (this is annoyingly duplicated with end-to-end...)
      if (parsed.image_data) {
        const filename = params.saveImageDataTo + '.svg';
        console.log(` -> Writing image (raw SVG from image_data) to ${filename}`)
        fs.writeFileSync(filename, parsed.image_data)

      } else if (parsed.image) {
        const rawFilename = params.saveImageDataTo + '.datauri'
        console.log(` -> Writing raw .image datauri to ${rawFilename}`)
        fs.writeFileSync(rawFilename, parsed.image)

        const [contentType, base64data] = parsed.image.split(',')

        if (contentType === 'data:image/bmp;base64') {
          const filename = params.saveImageDataTo + '.bmp'
          console.log(` -> Writing image (BMP from image) to ${filename}`)
          fs.writeFileSync(filename, Buffer.from(base64data, 'base64'))

        } else if (contentType === 'data:image/svg;base64') {
          const filename = params.saveImageDataTo + '.svg'
          console.log(` -> Writing image (SVG from image) to ${filename}`)
          fs.writeFileSync(filename, Buffer.from(base64data, 'base64'))

        }
      } else {
        throw new Error('no image or image_data!')
      }
    }
  });
