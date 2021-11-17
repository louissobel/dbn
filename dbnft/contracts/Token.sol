//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "./BitmapHeader.sol";

// Factor out drawing reads / writes
library Token {
    struct Metadata { 
       string name;
       string description;
       string external_url;
       string drawing_address;
    }
}
