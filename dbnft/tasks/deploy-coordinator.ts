const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')

import { task } from "hardhat/config";

task("deploy-coordinator", "Deploys the DBN coordinator")
  .setAction(async ({ file, output }) => {
    const hre = require("hardhat");
    await hre.run("compile");

    var baseExternalURL;
    var openSeaProxyRegistry;
    switch (hre.network.name) {
      case 'localhost':
        baseExternalURL = 'http://localhost:3000/dbnft/'
        openSeaProxyRegistry = "0x0000000000000000000000000000000000000000";
        break;
      case 'rinkeby':
        baseExternalURL = 'https://testnet.dbnft.io/dbnft/'
        openSeaProxyRegistry = '0xf57b2c51ded3a29e6891aba85459d600256cf317';
        break;
      case 'mainnet':
        baseExternalURL = 'https://dbnft.io/dbnft/';
        openSeaProxyRegistry = '0xa5409ec958c83c3f309868babaca7c86dcb077c1';
        throw new Error("mainnet not supported yet!")
      default:
        throw new Error("unhandled network: " + hre.network.name)
    }

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = await DBNCoordinator.deploy(baseExternalURL, openSeaProxyRegistry);
    await coordinator.deployed();
    const coordinatorDeployReceipt = await coordinator.deployTransaction.wait()

    console.log("Coordinator deployed to: ", coordinator.address, `(Gas used: ${coordinatorDeployReceipt.gasUsed.toString()})`);
    return coordinator.address
  });
