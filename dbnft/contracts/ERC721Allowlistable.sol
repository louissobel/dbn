
//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

import "./Drawing.sol";
import "./Token.sol";
import "./Serialize.sol"; 

abstract contract ERC721Allowlistable is ERC721, Ownable {
    /**********************************************************
    * Allowlist.
    *  - internally, I need to check in a mintTokenId call that the sender can do so
    *  - externally, I need to:
    *    - read the allowlist for tokens 0–100 to display status? (or some kind of admin panel...)
    *    - read the allowlist for a given _address_
    *    - update the allowlist
    * 
    *  - mapping token --> address _allowedMinterForTokenId
    *  - internal can just look at _allowedMinterForTokenId to check that sender == the person
    *  - externally, getting allowed address for a given token is enough
    *  - internally, we'll also _remove_ tokens from this list as things get minted
    * 
    *  Also, we _know_ that only [0, 100] are going to be allowlisted
    */
    mapping (uint256 => address) private _allowedMinterForTokenId;

    modifier onlyAllowlistedFor(uint256 tokenId) {
        require(_allowedMinterForTokenId[tokenId] == msg.sender, "NOT_ALLOWLISTED");
        _;
    }

    function getAllowedMinter(uint256 tokenId) public view returns(address) {
        return _allowedMinterForTokenId[tokenId];
    }

    function getAllowedTokenIds(address addr) public view returns(uint256[] memory) {
        uint8 count = 0;

        for (uint8 i = 0; i < 101; i++) {
            if (_allowedMinterForTokenId[i] == addr) {
                count++;
            }
        }

        uint256[] memory allowed = new uint256[](count);
        count = 0;
        for (uint8 i = 0; i < 101; i++) {
            if (_allowedMinterForTokenId[i] == addr) {
                allowed[count] = i;
                count++;
            }
        }

        return allowed;
    }

    struct AllowlistUpdate { 
       uint256 tokenId;
       address addr;
    }
    function updateAllowlist(AllowlistUpdate[] calldata input) public onlyOwner {
        for (uint i = 0; i < input.length; i++) {
            AllowlistUpdate calldata up = input[i];
            _allowedMinterForTokenId[up.tokenId] = up.addr;
        }
    }

    function _setAllowedMinter(uint256 tokenId, address minter) internal virtual {
    	_allowedMinterForTokenId[tokenId] = minter;
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, tokenId);

        if (from == address(0)) {
        	// Mint
        	if (_allowedMinterForTokenId[tokenId] != address(0)) {
        		_allowedMinterForTokenId[tokenId] = address(0);
        	}
        }
    }
}
