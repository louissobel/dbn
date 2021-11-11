const ethers = require('ethers')

import { task } from "hardhat/config";

task("open-contract", "Set the contract state to open")
  .addParam(
    "coordinator",
    "Address of coordinator contract (in hex)",
  )
  .setAction(async (params) => {
    const hre = require("hardhat");

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = DBNCoordinator.attach(params.coordinator)

    await coordinator.setContractOpen()
    console.log("Contract is now open!")
  });
