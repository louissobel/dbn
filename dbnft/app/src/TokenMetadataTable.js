import React from 'react';

import { Link } from "react-router-dom";

function TokenMetadataTable(props) {
  return(
    <table className="table dbn-token-metadata-table">
      <tbody>
        <tr>
          <th scope="row">Name</th>
          <td>DBNFT #{props.tokenId}</td>
        </tr>
        <tr>
          <th scope="row">Description</th>
          <td>{props.description}</td>
        </tr>
        <tr>
          <th scope="row">Drawing Address</th>
          <td>
            {/* TODO... link out to "view on etherscan?"... */}
            {props.address}
          </td>
        </tr>
        <tr>
          <th scope="row">URL</th>
          <td>
            <Link to={"/dbnft/" + props.tokenId}>
              {props.externalURL}
            </Link>
          </td>
        </tr>
      </tbody>
    </table>
  )
}

export default TokenMetadataTable;
