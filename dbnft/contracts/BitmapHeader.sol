//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

library BitmapHeader {

    bytes32 internal constant header1 = 0x424dd22a000000000000ca010000280000006500000065000000010008000000;
    bytes22 internal constant header2 = 0x00000000000000000000000000006500000000000000;

    function writeTo(bytes memory output) internal pure {

        assembly {
            mstore(add(output, 0x20), header1)
            mstore(add(output, 0x40), header2)
        }

        // palette index is "DBN" color : [0, 100]
        // map that to [0, 255] via:
        // 255 - ((255 * c) / 100)
        for (uint i = 0; i < 101; i++) {
            bytes1 c = bytes1(uint8(255 - ((255 * i) / 100)));
            uint o = i*4 + 54; // after the header
            output[o] = c;
            output[o + 1] = c;
            output[o + 2] = c;
        }

        
    }
}
