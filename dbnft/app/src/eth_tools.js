import DBNCoordinator from './contracts/DBNCoordinator'
import Eth  from 'web3-eth';

import frontendEnvironment from './frontend_environment'


// takes and returns hex
const prependDeployHeader = function(bytecode) {
  const inputLength = (bytecode.length - 2) / 2 // -2 takes off '0x'

  // TODO: throw error if input length is bigger than 0xFFFF
  const deployHeader = Buffer.from([
    // push length
    0x61, ((inputLength & 0xFF00) >> 8), (inputLength & 0xFF),

    // dup length
    0x80,

    // push code offset (same as length of deploy header...)
    0x60, 12,

    // push 0
    0x60, 0,

    // copy code into memory
    0x39,

    // get another zero on
    0x60, 0,

    // stack is now [0|length
    // code to deploy is at 0
    // so we're good to return :)
    0xF3
  ])

  return '0x' + deployHeader.toString('hex') + bytecode.slice(2)
}


const eth = new Eth(frontendEnvironment.config.ethNetwork)

const dbnCoordinator = new eth.Contract(
  DBNCoordinator,
  frontendEnvironment.config.coordinatorContractAddress,
)

export {
  prependDeployHeader,
  eth,
  dbnCoordinator,
}
