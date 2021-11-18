//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

import "./DBNERC721Enumerable.sol"; 
import "./OpenSeaTradable.sol"; 
import "./OwnerSignedTicketRestrictable.sol"; 

import "./Drawing.sol";
import "./Token.sol";
import "./Serialize.sol";

contract DBNCoordinator is Ownable, DBNERC721Enumerable, OpenSeaTradable, OwnerSignedTicketRestrictable {
    using Counters for Counters.Counter;
    using Strings for uint256;

    event DrawingDeployed(uint256 tokenId, address addr);

    // Config
    enum ContractMode { AllowlistOnly, Open }
    ContractMode private _contractMode;
    uint256 private _mintPrice;
    string private _baseExternalURI;

    // There's two ~types of tokenId:
    //  - 101 "allowlisted ones" <= 100
    //  - And "Open" ones > 100 (<= 10200)
    // Minting of the allowlisted ones is through mintTokenId
    // Minting of the Open ones is through plain mint
    uint256 private lastAllowlistedTokenId = 100;
    uint256 private lastTokenId = 10200;

    // Minting
    Counters.Counter private _tokenIds;
    mapping (uint256 => address) private _drawingAddressForTokenId;

    constructor(string memory baseExternalURI, address openSeaProxyRegistry) ERC721("Design By Numbers NFT", "DBNFT") {
        _baseExternalURI = baseExternalURI;
        _contractMode = ContractMode.AllowlistOnly;

        // first open token id is lastAllowlistedTokenId + 1
        _tokenIds._value = lastAllowlistedTokenId + 1;

        // initial mint price
        _mintPrice = 10000000 gwei; // 0.01 eth

        // set up the opensea proxy registry
        _setOpenSeaRegistry(openSeaProxyRegistry);
    }

    /*********
     * Config
     */
    function getContractMode() public view returns (ContractMode) {
        return _contractMode;
    }

    function setContractMode(ContractMode mode) public onlyOwner {
        _contractMode = mode;
    }

    function setMintPrice(uint256 price) public onlyOwner {
        _mintPrice = price;
    }

    function withdraw() public onlyOwner {
        address payable to = payable(msg.sender);
        to.transfer(address(this).balance);
    }

    /*********
     * Minting
     */
    function mint(bytes memory bytecode) payable public {
        require(_contractMode == ContractMode.Open, "NOT_OPEN");
        require(msg.value >= _mintPrice, "WRONG_PRICE");

        uint256 tokenId = _tokenIds.current();
        require(tokenId <= lastTokenId, 'SOLD_OUT');
        _tokenIds.increment();

        _mintAtTokenId(bytecode, tokenId);
    }

    function mintTokenId(
        bytes memory bytecode,
        uint256 tokenId,
        uint256 ticketId,
        bytes memory signature
    ) public onlyWithTicketFor(tokenId, ticketId, signature) {
        require(tokenId <= lastAllowlistedTokenId, 'WRONG_TOKENID_RANGE');

        _mintAtTokenId(bytecode, tokenId);
    }

    // private one they both call into
    function _mintAtTokenId(
        bytes memory bytecode,
        uint256 tokenId
    ) internal returns (address) {
        address addr = Drawing.deploy(bytecode, tokenId);

        _drawingAddressForTokenId[tokenId] = addr;

        // sender gets the token
        _safeMint(msg.sender, tokenId);

        emit DrawingDeployed(tokenId, addr);
        return addr;
    }

    // Override isApprovedForAll to include check for operator being
    // operator is owner's OpenSea proxy (for gasless trading)
    function isApprovedForAll(
        address owner,
        address operator
    ) public view override returns (bool) {
        return super.isApprovedForAll(owner, operator) || _isOwnersOpenSeaProxy(owner, operator);
    }

    /*********
     * Token Readers
     */
    function _addressForToken(uint256 tokenId) internal view returns (address) {
        address addr = _drawingAddressForTokenId[tokenId];
        require(addr != address(0), "UNKNOWN_ID");

        return addr;
    }

    function _externalURL(uint256 tokenId) internal view returns (string memory) {
        return string(abi.encodePacked(_baseExternalURI, tokenId.toString()));
    }

    function _getMetadata(uint256 tokenId, address addr) internal view returns (Token.Metadata memory) {
        string memory tokenIdAsString = tokenId.toString();

        return Token.Metadata(
            string(abi.encodePacked("DBNFT #", tokenIdAsString)),
            string(Drawing.description(addr)),
            string(abi.encodePacked(_baseExternalURI, tokenIdAsString)),
            uint256(uint160(addr)).toHexString()
        );
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        address addr = _addressForToken(tokenId);
        (, bytes memory bitmapData) = Drawing.render(addr);

        Token.Metadata memory metadata = _getMetadata(tokenId, addr);
        return Serialize.tokenURI(bitmapData, metadata);
    }

    function tokenMetadata(uint256 tokenId) public view returns (string memory) {
        address addr = _addressForToken(tokenId);
        Token.Metadata memory metadata = _getMetadata(tokenId, addr);
        return Serialize.metadataAsJSON(metadata);
    }

    function tokenCode(uint256 tokenId) public view returns (bytes memory) {
        address addr = _addressForToken(tokenId);
        return addr.code;
    }

    function renderToken(uint256 tokenId) public view returns (uint256, bytes memory) {
        address addr = _addressForToken(tokenId);
        return Drawing.render(addr);
    }


    function mintedAllowlistedTokens() public view returns (uint256[] memory) {
        uint8 count = 0;
        for (uint8 i = 0; i <= lastAllowlistedTokenId; i++) {
            if (_exists(i)) {
                count++;
            }
        }

        uint256[] memory result = new uint256[](count);
        count = 0;
        for (uint8 i = 0; i <= lastAllowlistedTokenId; i++) {
            if (_exists(i)) {
                result[count] = i;
                count++;
            }
        }

        return result;
    }
}
