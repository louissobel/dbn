const { expect } = require("chai");
const { ethers } = require("hardhat");

const fs = require('fs')
const VM = require('@ethereumjs/vm').default
const { BN } = require('ethereumjs-util')

describe("Draw#initializeBitmap", function () {
  const cases = [
    [0, 0],
    [20, 20],
    [100, 100],
    [105, 100],
    [-5, 0]
  ]

  cases.forEach(function([ input, output]) {
    it(`Should correctly draw paper ${input}`, async function () {
      const contract = fs.readFileSync('artifacts/contracts/RenderDBNTestArtifact.eth')
      const vm = new VM()

      const runOpts = {
        code: contract,
        gasLimit: new BN(0xffffffff),
        data: Buffer.from([0xAE, input]),
      }
      const result = await vm.runCode(runOpts)

      if (result.exceptionError) {
        throw new Error("failure: " + result.exceptionError.error)
      }

      const raw = "0x" + result.returnValue.toString('hex')
      const coder = new ethers.utils.AbiCoder()
      const value = coder.decode(["bytes"], raw)[0]
      const bitmapBuffer = Buffer.from(value.slice(2), 'hex')
      // 14 + 40 + 404 is offset to pixel data

      const pixelData = bitmapBuffer.slice(14 + 40 + 404)
      expect(pixelData).to.eql(
        Buffer.from(Array(104 * 101).fill(output))
      )
    });
  })
});
