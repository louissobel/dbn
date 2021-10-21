//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";

import "./Base64.sol";

contract LibraryTestHarness { 
    function base64encode(bytes memory input) public view returns (bytes memory) {
        return Base64.encode(input);
    }
}
