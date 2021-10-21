const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')

import { task } from "hardhat/config";

task("deploy-coordinator", "Deploys the DBN coordinator")
  .setAction(async ({ file, output }) => {
    const hre = require("hardhat");

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = await DBNCoordinator.deploy();
    await coordinator.deployed();
    const coordinatorDeployReceipt = await coordinator.deployTransaction.wait()

    console.log("Coordinator deployed to: ", coordinator.address, `(Gas used: ${coordinatorDeployReceipt.gasUsed.toString()})`);
    return coordinator.address
  });
