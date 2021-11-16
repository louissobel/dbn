const { expect } = require("chai");
const { ethers } = require("hardhat");

const fs = require('fs')
const VM = require('@ethereumjs/vm').default
const { BN } = require('ethereumjs-util')

describe("Draw#initializeBitmap", function () {
  const cases = [
    [101, "0x424dd22a000000000000ca01000028000000650000006500000001000800000000000000000000000000000000006500000000000000ffffff00fdfdfd00fafafa00f8f8f800f5f5f500f3f3f300f0f0f000eeeeee00ebebeb00e9e9e900e6e6e600e3e3e300e1e1e100dedede00dcdcdc00d9d9d900d7d7d700d4d4d400d2d2d200cfcfcf00cccccc00cacaca00c7c7c700c5c5c500c2c2c200c0c0c000bdbdbd00bbbbbb00b8b8b800b6b6b600b3b3b300b0b0b000aeaeae00ababab00a9a9a900a6a6a600a4a4a400a1a1a1009f9f9f009c9c9c00999999009797970094949400929292008f8f8f008d8d8d008a8a8a00888888008585850083838300808080007d7d7d007b7b7b00787878007676760073737300717171006e6e6e006c6c6c00696969006666660064646400616161005f5f5f005c5c5c005a5a5a00575757005555550052525200505050004d4d4d004a4a4a00484848004545450043434300404040003e3e3e003b3b3b00393939003636360033333300313131002e2e2e002c2c2c00292929002727270024242400222222001f1f1f001d1d1d001a1a1a00171717001515150012121200101010000d0d0d000b0b0b0008080800060606000303030000000000"],
  ]

  cases.forEach(function([ input, output ]) {
    it(`Should correctly initializeBitmap with side ${input}`, async function () {
      const contract = fs.readFileSync('artifacts/contracts/RenderDBNTestArtifact.eth')
      const vm = new VM()

      const runOpts = {
        code: contract,
        gasLimit: new BN(0xffffffff),
        data: Buffer.from([0xB1]),
      }
      const result = await vm.runCode(runOpts)

      if (result.exceptionError) {
        throw new Error("failure: " + result.exceptionError.error)
      }

      const raw = "0x" + result.returnValue.toString('hex')
      const coder = new ethers.utils.AbiCoder()
      const value = coder.decode(["bytes"], raw)[0]

      expect(value).to.eq(output)
    });
  })
});
