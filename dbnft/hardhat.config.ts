require("@nomiclabs/hardhat-waffle");
import "@nomiclabs/hardhat-ganache";

require("./tasks/assemble")
require("./tasks/assemble-and-run")

require("./tasks/end-to-end-render-drawing")

require("./tasks/deploy-coordinator")
require("./tasks/deploy-helper")
require("./tasks/get-token-uri")

require("./tasks/open-contract")

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: {
    version: "0.8.4",
    settings: {
      optimizer: {
        enabled: true,
        runs: 1000,
      },
    }
  },

};
