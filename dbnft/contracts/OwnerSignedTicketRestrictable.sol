
//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

abstract contract OwnerSignedTicketRestrictable is Ownable {
    /**********************************************************
    * Use ECDSA to validate incoming signature
    * (and some helper functions)
    */
    mapping (uint256 => bool) private _revokedTickets;

    modifier onlyWithTicketFor(uint256 tokenId, uint256 ticketId, bytes memory signature) {
        checkTicket(msg.sender, tokenId, ticketId, signature);
        _;
    }

    function checkTicket(
        address minter,
        uint256 tokenId,
        uint256 ticketId,
        bytes memory signature
    ) public view {
        bytes memory params = abi.encode(
            address(this),
            minter,
            tokenId,
            ticketId
        );
        address addr = ECDSA.recover(
            ECDSA.toEthSignedMessageHash(keccak256(params)),
            signature
        );

        require(addr == owner(), "BAD_SIGNATURE");
        require(!_revokedTickets[ticketId], "TICKET_REVOKED");
    }

    function revokeTicket(uint256 ticketId) public onlyOwner {
        _revokedTickets[ticketId] = true;
    }

}
