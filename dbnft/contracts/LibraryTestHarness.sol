//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";

import "./Base64.sol";
import "./BitmapHeader.sol";

contract LibraryTestHarness { 
    function base64encode(bytes memory input) public pure returns (bytes memory) {
        return Base64.encode(input);
    }

    function bitmapHeader() public pure returns (bytes memory) {
        bytes memory output = new bytes(14 + 40 + 404);
        BitmapHeader.writeTo(output);
        return output;
    }
}
