const ethers = require('ethers')

import { task } from "hardhat/config";

task("set-image-metadata-mode", "Set the image mode")
  .addParam(
    "coordinator",
    "Address of coordinator contract (in hex)",
  )
  .addParam(
    'mode',
    '[image_data_svg|image_bmp|image_svg]',
  )
  .setAction(async (params) => {
    const hre = require("hardhat");

    const DBNCoordinator = await hre.ethers.getContractFactory("DBNCoordinator");
    const coordinator = DBNCoordinator.attach(params.coordinator)

    let v;
    switch (params.mode) {
      case 'image_data_svg':
        v = 0;
        break;
      case 'image_bmp':
        v = 1;
        break;
      case 'image_svg':
        v = 2;
        break;
      default:
        throw new Error('unrecognized image mode: ' + params.mode)
    }

    await coordinator.setImageMetadataMode(v);
    console.log("OK")

  });
