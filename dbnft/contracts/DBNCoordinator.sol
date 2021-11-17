//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

import "./ERC721Allowlistable.sol";
import "./DBNERC721Enumerable.sol"; 

import "./Drawing.sol";
import "./Token.sol";
import "./Serialize.sol";

contract DBNCoordinator is Ownable, DBNERC721Enumerable, ERC721Allowlistable {
    using Counters for Counters.Counter;
    using Strings for uint256;

    event DrawingDeployed(uint256 tokenId, address addr);

    // Config
    enum ContractMode { AllowlistOnly, Open }
    ContractMode private _contractMode;
    uint256 private _mintPrice;
    string private _baseExternalURI;

    // Minting
    Counters.Counter private _tokenIds;
    mapping (uint256 => address) private _drawingAddressForTokenId;

    constructor(string memory baseExternalURI) ERC721("Design By Numbers NFT", "DBNFT") {
        _baseExternalURI = baseExternalURI;
        _contractMode = ContractMode.AllowlistOnly;

        // Initialize this...
        _setAllowedMinter(0, _msgSender());
        _setAllowedMinter(1, _msgSender());
        _setAllowedMinter(2, _msgSender());
        _setAllowedMinter(3, _msgSender());
        _setAllowedMinter(4, _msgSender());
        _setAllowedMinter(5, _msgSender());
        _setAllowedMinter(6, _msgSender());
        _setAllowedMinter(7, _msgSender());
        _setAllowedMinter(8, _msgSender());
        _setAllowedMinter(9, _msgSender());

        // first open token id is 101
        _tokenIds._value = 101;

        // initial mint price
        _mintPrice = 10000000 gwei; // 0.01 eth
    }

    /*********
     * Config
     */
    function getContractMode() public view returns (ContractMode) {
        return _contractMode;
    }

    function setContractOpen() public onlyOwner {
        _contractMode = ContractMode.Open;
    }

    function setMintPrice(uint256 price) public onlyOwner {
        _mintPrice = price;
    }

    function withdraw() public onlyOwner {
        address payable to = payable(msg.sender);
        to.transfer(address(this).balance);
    }

    // This needs to be defined as an override to
    // explicitly resolve the inheritence ¯\_(ツ)_/¯
    function supportsInterface(bytes4 interfaceId) public view override(DBNERC721Enumerable, ERC721) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    /*********
     * Minting
     */
    function mint(bytes memory bytecode) payable public returns (address) {
        require(_contractMode == ContractMode.Open, "NOT_OPEN");
        require(msg.value == _mintPrice, "WRONG_PRICE");

        uint256 tokenId = _tokenIds.current();
        require(tokenId < 10201, 'SOLD_OUT');

        _tokenIds.increment();

        return _mintAtTokenId(bytecode, tokenId);
    }

    function mintTokenId(
        bytes memory bytecode,
        uint256 tokenId
    ) public onlyAllowlistedFor(tokenId) returns (address) {
        return _mintAtTokenId(bytecode, tokenId);
    }

    // private one they both call into
    function _mintAtTokenId(
        bytes memory bytecode,
        uint256 tokenId
    ) internal returns (address) {
        // Inject the token id into the bytecode
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

        _drawingAddressForTokenId[tokenId] = addr;

        // sender gets the token
        _safeMint(msg.sender, tokenId);

        emit DrawingDeployed(tokenId, addr);
        return addr;
    }

    // This needs to be defined as an override to
    // explicitly resolve the inheritence ¯\_(ツ)_/¯
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal override(DBNERC721Enumerable, ERC721Allowlistable) {
        super._beforeTokenTransfer(from, to, tokenId);
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
}
