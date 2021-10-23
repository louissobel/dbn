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
  });
