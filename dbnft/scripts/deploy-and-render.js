const hre = require("hardhat");

async function main() {

  const DBNCode = await hre.ethers.getContractFactory("DBNCode");

  debugger;

  const dbncode = await DBNCode.deploy();

  await dbncode.deployed();


  console.log("DBNCode deployed to:", dbncode.address);

  console.log("Render result: ", (await dbncode.render()))
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
