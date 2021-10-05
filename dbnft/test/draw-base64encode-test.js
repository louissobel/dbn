const { expect } = require("chai");
const { ethers } = require("hardhat");

const fs = require('fs')
const VM = require('@ethereumjs/vm').default
const { BN } = require('ethereumjs-util')

describe("Draw#base64encode", function () {
  const cases = [
    ["", ""],
    ["I", "SQ=="],
    ["12", "MTI="],
    ["RTA", "UlRB"],
    ["hello!", "aGVsbG8h"],
    [Buffer.from([0, 101, 255]), "AGX/"],
    ["012345678901234567890123456789", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5"],
    ["012345678901234567890123456789.", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5Lg=="],
    ["012345678901234567890123456789..", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5Li4="],
    ["012345678901234567890123456789...", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5Li4u"],
    ["hello!hello!hello!hello!", "aGVsbG8haGVsbG8haGVsbG8haGVsbG8h"],
    ["hello!hello!hello!hello!+", "aGVsbG8haGVsbG8haGVsbG8haGVsbG8hKw=="],
    [
      "einah7eich0ofah2Eu8aithaefahxu4theiSaeHahpichah3Ic0Ung6phei7ohteitheekaet7ShahYeezee8thaetei5quahgh8kiejog9ahm1cheeGohkeachahTahthah6aequof1Dae6ih6aeco7Ochufeb5aotei8iunein3pah1goZ9faiv0eo2paenooWiwe1PooNg6thooFai2kooZahwohshaep9aikohtei5Xothie5ok6aewoojeiw1uix9ooxainie2eec9Uquaa3HeiBei3nohchizeiyiGhei8izae4keangah9kix",
      "ZWluYWg3ZWljaDBvZmFoMkV1OGFpdGhhZWZhaHh1NHRoZWlTYWVIYWhwaWNoYWgzSWMwVW5nNnBoZWk3b2h0ZWl0aGVla2FldDdTaGFoWWVlemVlOHRoYWV0ZWk1cXVhaGdoOGtpZWpvZzlhaG0xY2hlZUdvaGtlYWNoYWhUYWh0aGFoNmFlcXVvZjFEYWU2aWg2YWVjbzdPY2h1ZmViNWFvdGVpOGl1bmVpbjNwYWgxZ29aOWZhaXYwZW8ycGFlbm9vV2l3ZTFQb29OZzZ0aG9vRmFpMmtvb1phaHdvaHNoYWVwOWFpa29odGVpNVhvdGhpZTVvazZhZXdvb2plaXcxdWl4OW9veGFpbmllMmVlYzlVcXVhYTNIZWlCZWkzbm9oY2hpemVpeWlHaGVpOGl6YWU0a2VhbmdhaDlraXg=",
    ],
    [
      Buffer.from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255]),
      'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==',
    ],
    [
      Buffer.from([0, 16, 131, 16, 81, 135, 32, 146, 139, 48, 211, 143, 65, 20, 147, 81, 85, 151, 97, 150, 155, 113, 215, 159, 130, 24, 163, 146, 89, 167, 162, 154, 171, 178, 219, 175, 195, 28, 179, 211, 93, 183, 227, 158, 187, 243, 223, 191]),
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
    ]
  ]

  cases.forEach(function([ input, output ]) {
    it(`Should correctly base64encode ${input}`, async function () {
      const contract = fs.readFileSync('artifacts/contracts/Draw.eth')
      const vm = new VM()

      const runOpts = {
        code: contract,
        gasLimit: new BN(0xffffffff),
        data: Buffer.concat([Buffer.from([0x64]), Buffer.from(input)]),
      }
      const result = await vm.runCode(runOpts)

      if (result.exceptionError) {
        throw new Error("failure: " + result.exceptionError.error)
      }

      const raw = "0x" + result.returnValue.toString('hex')
      const coder = new ethers.utils.AbiCoder()
      const value = coder.decode(["string"], raw)[0]

      expect(value).to.eq(output)
    });
  })
});
