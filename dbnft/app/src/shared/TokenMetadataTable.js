import React from 'react';

import { Link } from "react-router-dom";

import frontendEnvironment from '../frontend_environment'

function TokenMetadataTable(props) {

  const etherscanURL = frontendEnvironment.config.etherscanBase + "/address/" + props.address;

  return(
    <table className="table dbn-token-metadata-table border-dark">
      <tbody>
        <tr>
          <th scope="row">Name</th>
          <td>DBNFT #{props.tokenId}</td>
        </tr>
        <tr>
          <th scope="row">Creator</th>
          <td>{props.creator}</td>
        </tr>
        <tr>
          <th scope="row">Description</th>
          <td>{props.description}</td>
        </tr>
        <tr>
          <th scope="row">Drawing Address</th>
          <td>
            <a href={etherscanURL}>
              {props.address}
            </a>
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

        {props.ipfsCID &&
          <tr>
            <th scope="row">Source Code</th>
            <td>
              {"ipfs://" + props.ipfsCID}
            </td>
          </tr>
        }
      </tbody>
    </table>
  )
}

export default TokenMetadataTable;
