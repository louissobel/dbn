const ethers = require('ethers')

import { task } from "hardhat/config";

task("allowlist", "Read / write the allowlist")
  .addParam(
    "coordinator",
    "Address of coordinator contract (in hex)",
  )
  .addOptionalParam(
    'updates',
    'comma-separated, colon delimited, tokenId:addr pairs'
  )
  .setAction(async (params) => {
    const hre = require("hardhat");

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = DBNCoordinator.attach(params.coordinator)

    if (params.updates) {
      let updateSpecs = params.updates.split(',')
      let updates = updateSpecs.map((s: string) => {
        let parts = s.split(':')
        let up = [
          parseInt(parts[0]),
          parts[1]
        ]
        console.log(up)
        return up
      })

      await coordinator.updateAllowlist(updates)
    }

    // read
    for (let i = 0; i<101; i++) {
      const allowlistedAddress = await coordinator.getAllowedMinter(i)
      console.log(`#${i}: ${allowlistedAddress}`)
    }
  });
