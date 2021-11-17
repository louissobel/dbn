//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "./Token.sol";
import "./Base64.sol";

// Factor out drawing reads / writes
library Serialize {
    function tokenURI(bytes memory bitmapData, Token.Metadata memory metadata) internal pure returns (string memory) {
        // Use the "SVG DataURI not-base64-encoded" approach
        string memory imageKey = "image";
        bytes memory imageData = _svgDataURI(bitmapData);

        string memory fragment = _metadataJSONFragmentWithoutImage(metadata);
        return string(abi.encodePacked(
            'data:application/json,',
            fragment,
            // image data :)
            '","', imageKey, '":"', imageData, '"}'
        ));
    }

    function metadataAsJSON(Token.Metadata memory metadata) internal pure returns (string memory) {
        string memory fragment = _metadataJSONFragmentWithoutImage(metadata);
        return string(abi.encodePacked(
            fragment,
            '"}'
        ));
    }

    function _metadataJSONFragmentWithoutImage(Token.Metadata memory metadata) internal pure returns (string memory) {
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

    // Ok, so there's a few ways we could embed the image:
    // - raw data URL base64-encoded bitmap in `image`
    // - bitmap embedded in SVG in `image_data`
    // - SVG data URL in `image` (base64 encoded)
    function _base64BMP(bytes memory bitmapData) internal pure returns (bytes memory) {
        return abi.encodePacked(
            "data:image/bmp;base64,",
            Base64.encode(bitmapData)
        );
    }

    function _imageEmbeddedInSVG(bytes memory bitmapData) internal pure returns (bytes memory) {
        return abi.encodePacked(
            "<svg xmlns='http://www.w3.org/2000/svg' width='303' height='303'><image width='303' height='303' style='image-rendering: pixelated' href='",
            _base64BMP(bitmapData),
            "'/></svg>"
        );
    }

    function _base64SVG(bytes memory bitmapData) internal pure returns (bytes memory) {
        return abi.encodePacked(
            "data:image/svg+xml;base64,",
            Base64.encode(_imageEmbeddedInSVG(bitmapData))
        );
    }

    function _svgDataURI(bytes memory bitmapData) internal pure returns (bytes memory) {
        return abi.encodePacked(
            "data:image/svg+xml,",
            _imageEmbeddedInSVG(bitmapData)
        );
    }
}
