//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "./BitmapHeader.sol";

// Factor out Drawing contract interaction
library Drawing {
    function deploy(bytes memory bytecode, uint256 tokenId) internal returns (address) {
        // First, inject the token id into the bytecode.s
        // The end of the bytecode is [2 bytes token id][32 bytes ipfs hash]
        // (and we get the tokenID in in bigendian)
        bytecode[bytecode.length - 32 - 2] = bytes1(uint8((tokenId & 0xFF00) >> 8));
        bytecode[bytecode.length - 32 - 1] = bytes1(uint8(tokenId & 0xFF));

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

        So no matter what, we want to "assert" the addr is not zero
        */
        assert(addr != address(0));

        return addr;
    }

    function render(address addr) internal view returns (uint256, bytes memory) {
        uint bitmapLength = 10962;
        uint headerLength = 40 + 14 + 404;
        uint pixelDataLength = (10962 - headerLength);

        bytes memory result = new bytes(bitmapLength);
        bytes memory input = hex"BD";

        uint256 startGas = gasleft();

        BitmapHeader.writeTo(result);
        uint resultOffset = 0x20 + headerLength; // after the header (and 0x20 for the dynamic byte length)

        bool success;
        assembly {
            success := staticcall(
                gas(),
                addr,
                add(input, 0x20),
                1,
                add(result, resultOffset),
                pixelDataLength // only allow up to a full bitmap back
            )
        }

        // this overestimates _some_, but that's fine
        uint256 endGas = gasleft();

        require(success, "RENDER_FAIL");

        return ((startGas - endGas), result);
    }

    function description(address addr) internal view returns (string memory) {
        (bool success, bytes memory desc) = addr.staticcall(hex"DE");
        require(success, "DESCRIPTION_FAIL");
        return string(desc);
    }
}
