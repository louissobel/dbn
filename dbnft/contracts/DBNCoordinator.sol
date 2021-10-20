//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

import "./Base64.sol";

contract DBNCoordinator is ERC721 {

    event DrawingDeployed(address addr);

    constructor() ERC721("DBN NFT", "DBNFT") {}

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

        // sender gets the token
        _safeMint(msg.sender, uint256(uint160(addr)));
        emit DrawingDeployed(addr);
        return addr;
    }

    function _render(address addr) internal view returns (bytes memory) {
        // TODO: use the openzeppelin wrapping helpers?
        (bool success, bytes memory result) = addr.staticcall("");

        require(success, "failure render call");

        return result;
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        address addr = address(uint160(tokenId));
        bytes memory bitmapData = _render(addr);

        return _generateURI(bitmapData);
    }

    function _generateURI(bytes memory bitmapData) internal view returns (string memory) {
        return string(abi.encodePacked(
            'data:application/json,'
            // name
            '{"name":"'
                "Eth",

            // description
            '","description":"',
                "DBNFT0",

            // external_url
            '","external_url":"',
                "https://dbnft.io/nft/0",

            // attributes
            '","attributes":',
                "[]",

            // image data :)
            ',"image":"',
                "data:image/bmp;base64,",
                string(Base64.encode(bitmapData)),
            '"}'
        ));

    }
}
