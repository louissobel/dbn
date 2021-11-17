//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "./BitmapHeader.sol";

// Factor out drawing reads / writes
library Drawing {
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
