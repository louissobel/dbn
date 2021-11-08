//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

import "./Base64.sol";

contract DBNCoordinator is ERC721, IERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    using Strings for uint256;

    event DrawingDeployed(uint256 tokenId, address addr, string externalURL);

    Counters.Counter private _tokenIds;
    uint256[] private _allTokens;
    mapping(address => mapping(uint256 => uint256)) private _ownedTokens;
    mapping(uint256 => uint256) private _ownedTokensIndex;

    mapping (uint256 => address) private _drawingAddressForTokenId;
    string private _baseExternalURI;

    constructor(string memory baseExternalURI) ERC721("Design By Numbers NFT", "DBNFT") {
        _baseExternalURI = baseExternalURI;
    }

    /**********************************************************
    Enumeration Interface
    We're not using ERC721Enumerable from openzeppelin because it:
     - is bigger than we need due to burnable support
     - doesn't have a way to easily return all tokenIDs, which we want for the gallery

    All this code is copied from OpenZeppelin's ERC721Enumerable implementation though
    */
    function supportsInterface(bytes4 interfaceId) public view virtual override(IERC165, ERC721) returns (bool) {
        return interfaceId == type(IERC721Enumerable).interfaceId || super.supportsInterface(interfaceId);
    }

    function tokenOfOwnerByIndex(address owner, uint256 index) public view virtual override returns (uint256) {
        require(index < ERC721.balanceOf(owner), "owner index out of bounds");
        return _ownedTokens[owner][index];
    }

    function totalSupply() public view virtual override returns (uint256) {
        return _allTokens.length;
    }

    function tokenByIndex(uint256 index) public view virtual override returns (uint256) {
        require(index < totalSupply(), "global index out of bounds");
        return _allTokens[index];
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, tokenId);

        if (from == address(0)) {
            // Mint
            _addTokenToAllTokensEnumeration(tokenId);
        } else if (from != to) {
            // Transfer out
            _removeTokenFromOwnerEnumeration(from, tokenId);
        }

        if (to != from) {
            // Transfer In (also handles Mint)
            _addTokenToOwnerEnumeration(to, tokenId);
        }
    }

    function _addTokenToAllTokensEnumeration(uint256 tokenId) private {
        _allTokens.push(tokenId);
    }

    function _removeTokenFromOwnerEnumeration(address from, uint256 tokenId) private {
        // To prevent a gap in from's tokens array, we store the last token in the index of the token to delete, and
        // then delete the last slot (swap and pop).

        uint256 lastTokenIndex = ERC721.balanceOf(from) - 1;
        uint256 tokenIndex = _ownedTokensIndex[tokenId];

        // When the token to delete is the last token, the swap operation is unnecessary
        if (tokenIndex != lastTokenIndex) {
            uint256 lastTokenId = _ownedTokens[from][lastTokenIndex];

            _ownedTokens[from][tokenIndex] = lastTokenId; // Move the last token to the slot of the to-delete token
            _ownedTokensIndex[lastTokenId] = tokenIndex; // Update the moved token's index
        }

        // This also deletes the contents at the last position of the array
        delete _ownedTokensIndex[tokenId];
        delete _ownedTokens[from][lastTokenIndex];
    }

    function _addTokenToOwnerEnumeration(address to, uint256 tokenId) private {
        uint256 length = ERC721.balanceOf(to);
        _ownedTokens[to][length] = tokenId;
        _ownedTokensIndex[tokenId] = length;
    }

    /*
     * END ENUMERATION METHODS
     *******************************************/




    // TODO: for now, minting is locked down to just owner
    function deploy(bytes memory bytecode) public onlyOwner returns (address) {

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

        uint256 tokenId = _tokenIds.current();
        _tokenIds.increment();

        _drawingAddressForTokenId[tokenId] = addr;

        // sender gets the token
        _safeMint(msg.sender, tokenId);

        emit DrawingDeployed(tokenId, addr, _externalURL(tokenId));
        return addr;
    }

    function _render(address addr) internal view returns (bytes memory) {
        // TODO: use the openzeppelin wrapping helpers?
        (bool success, bytes memory result) = addr.staticcall("");
        require(success, "failure render call");

        return result;
    }

    struct Metadata { 
       string name;
       string description;
       string external_url;
       string drawing_address;
    }

    function _externalURL(uint256 tokenId) internal view returns (string memory) {
        return string(abi.encodePacked(_baseExternalURI, tokenId.toString()));
    }

    function _getMetadata(uint256 tokenId, address addr) internal view returns (Metadata memory) {
        // get description (todo: should we wrap this in some openzeppelin helper?)
        (bool success, bytes memory description) = addr.staticcall(hex"DE");
        require(success, "DESCRIPTION_FAIL");

        string memory tokenIdAsString = tokenId.toString();
        return Metadata(
            string(abi.encodePacked("DBNFT #", tokenIdAsString)),
            string(description),
            _externalURL(tokenId),
            uint256(uint160(addr)).toHexString()
        );
    }

    function _addressForToken(uint256 tokenId) internal view returns (address) {
        address addr = _drawingAddressForTokenId[tokenId];
        require(addr != address(0), "UNKNOWN_ID");

        return addr;
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        address addr = _addressForToken(tokenId);
        bytes memory bitmapData = _render(addr);

        Metadata memory metadata = _getMetadata(tokenId, addr);
        return _generateURI(bitmapData, metadata);
    }

    function tokenMetadata(uint256 tokenId) public view returns (string memory) {
        address addr = _addressForToken(tokenId);
        Metadata memory metadata = _getMetadata(tokenId, addr);
        return _generateMetadataJSON(metadata);
    }

    function tokenCode(uint256 tokenId) public view returns (bytes memory) {
        address addr = _addressForToken(tokenId);
        return addr.code;
    }

    function allTokens() public view returns (uint256[] memory) {
        return _allTokens;
    }

    function _metadataJSONFragmentWithoutImage(Metadata memory metadata) internal pure returns (string memory) {
        // TODO... what about the encoding of this?
        // do I need to base64? mark the charset?
        return string(abi.encodePacked(
            // name
            '{"name":"',
                metadata.name,

            // description
            '","description":"',
                metadata.description,

            // external_url
            '","external_url":"',
                metadata.external_url,

            // code address
            '","drawing_address":"',
                metadata.drawing_address
        ));
    }


    function _generateURI(bytes memory bitmapData, Metadata memory metadata) internal pure returns (string memory) {
        string memory fragment = _metadataJSONFragmentWithoutImage(metadata);
        return string(abi.encodePacked(
            'data:application/json,',
            fragment,
            // image data :)
            '","image_data":"',
                "<svg xmlns='http://www.w3.org/2000/svg' width='303' height='303'><image width='303' height='303' style='image-rendering: pixelated' href='"
                "data:image/bmp;base64,",
                string(Base64.encode(bitmapData)),
                "'/></svg>"
            '"}'
        ));
    }

    function _generateMetadataJSON(Metadata memory metadata) internal pure returns (string memory) {
        string memory fragment = _metadataJSONFragmentWithoutImage(metadata);
        return string(abi.encodePacked(
            fragment,
            '"}'
        ));
    }
}
