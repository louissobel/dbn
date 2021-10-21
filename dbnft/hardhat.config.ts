require("@nomiclabs/hardhat-waffle");
import "@nomiclabs/hardhat-ganache";

require("./tasks/assemble")
require("./tasks/assemble-and-run")

require("./tasks/end-to-end-render-drawing")


require("./tasks/deploy-coordinator")

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.8.4",
};
