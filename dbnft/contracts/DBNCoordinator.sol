//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";

contract DBNCoordinator {

    event DrawingDeployed(address addr);


    function deploy(bytes memory bytecode) public returns (address) {
        address addr;

        assembly {
            addr := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        /*
        if addr is zero, a few things could have happened:
            a) out-of-gas in the create (which gets forwarded [current*(63/64) - 32000])
            b) other exceptional halt (call stack too deep, invalid jump, etc)
            c) revert from the create

        in a): we should drain all existing gas and effectively bubble up the out of gas.
               this makes sure that gas estimators do the right thing
        in b): this is a nasty situation, so let's just drain away our gas anyway (true assert)
        in c): pretty much same as b) — this is a bug in the passed bytecode, and we should fail.
               that said, we _could_ check the μo return buffer for REVERT data, but no need for now. 
        */
        assert(addr != address(0));

        emit DrawingDeployed(addr);
        return addr;
    }

    function render(address addr) public view returns (bytes memory) {
        // TODO: use the openzeppelin wrapping helpers?
        (bool success, bytes memory result) = addr.staticcall("");

        require(success, "failure render call");

        return result;
    }
}
