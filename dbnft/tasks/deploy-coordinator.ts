const fs = require('fs')
const asm = require("@ethersproject/asm");

import { BN } from 'ethereumjs-util'
const ethers = require('ethers')

import { task } from "hardhat/config";

task("deploy-coordinator", "Deploys the DBN coordinator")
  .addOptionalParam(
    "owner",
    "Address to set as owner. If not set will be the deployer",
  )
  .addOptionalParam(
    "real",
    "If not set, will only print the params"
  )
  .setAction(async ({ owner, real }) => {
    const hre = require("hardhat");
    await hre.run("compile");

    const defaultOwner = (await hre.ethers.getSigners())[0].address
    let deployedOwner = owner || defaultOwner;

    var baseExternalURL;
    var openSeaProxyRegistry;
    var recipient;
    switch (hre.network.name) {
      case 'localhost':
        baseExternalURL = 'http://localhost:3000/dbnft/'
        openSeaProxyRegistry = "0x0000000000000000000000000000000000000000";
        recipient = deployedOwner;
        break;
      case 'rinkeby':
        baseExternalURL = 'https://testnet.dbnft.io/dbnft/'
        openSeaProxyRegistry = '0xf57b2c51ded3a29e6891aba85459d600256cf317';
        recipient = deployedOwner;
        break;
      case 'mainnet':
        baseExternalURL = 'https://dbnft.io/dbnft/';
        openSeaProxyRegistry = '0xa5409ec958c83c3f309868babaca7c86dcb077c1';
        recipient = '0x309FD9Dc50e465Dc6e2ECd20430C3497E009E6BC'
        throw new Error("mainnet not supported yet!")
      default:
        throw new Error("unhandled network: " + hre.network.name)
    }

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    if (!(real || hre.network.name === 'localhost')) {
      console.log("Dryrun deploy")
      console.log("Params:", [
        deployedOwner,
        baseExternalURL,
        recipient,
        openSeaProxyRegistry,
      ])
      return;
    }

    const coordinator = await DBNCoordinator.deploy(
      deployedOwner,
      baseExternalURL,
      recipient,
      openSeaProxyRegistry,
    );
    await coordinator.deployed();
    const coordinatorDeployReceipt = await coordinator.deployTransaction.wait()

    console.log("Coordinator deployed to: ", coordinator.address)
    console.log("Owner set to: ", deployedOwner)
    console.log(`Gas used: ${coordinatorDeployReceipt.gasUsed.toString()}`);
    return coordinator.address
  });
