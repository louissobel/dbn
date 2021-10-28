const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')

import { task } from "hardhat/config";

task("deploy-coordinator", "Deploys the DBN coordinator")
  .setAction(async ({ file, output }) => {
    const hre = require("hardhat");

    var baseExternalURL;
    switch (hre.network.name) {
      case 'localhost':
        baseExternalURL = 'http://localhost:3000/dbnft/'
        break;
      case 'rinkeby':
        baseExternalURL = 'https://testnet.dbnft.io/dbnft/'
        break;
      default:
        throw new Error("unhandled network: " + hre.network.name)
    }

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = await DBNCoordinator.deploy(baseExternalURL);
    await coordinator.deployed();
    const coordinatorDeployReceipt = await coordinator.deployTransaction.wait()

    console.log("Coordinator deployed to: ", coordinator.address, `(Gas used: ${coordinatorDeployReceipt.gasUsed.toString()})`);
    return coordinator.address
  });
