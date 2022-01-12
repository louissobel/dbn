import React from 'react';

import { Link } from "react-router-dom";
import { Icon } from '@iconify/react';

import frontendEnvironment from '../frontend_environment'
import twitterHandleForAddress from './twitterHandleForAddress'

function EtherscanLinkedAddress({address}) {
  const etherscanURL = frontendEnvironment.config.etherscanBase + "/address/" + address;

  return (
    <a href={etherscanURL}>{address}</a>
  )
}

function MaybeTwitterHandleLinkForAddress({address}) {
  const handle = twitterHandleForAddress[address];
  if (!handle) {
    return null;
  }

  return (
    <div>
      <Icon icon="mdi:twitter" />
      <a href={`https://twitter.com/${handle}`}>@{handle}</a>
    </div>
  )
}

function TokenMetadataTable(props) {
  return(
    <table className="table dbn-token-metadata-table border-dark">
      <tbody>
        <tr>
          <th scope="row">Name</th>
          <td>DBNFT #{props.tokenId}</td>
        </tr>
        <tr>
          <th scope="row">Creator</th>
          <td>
            <MaybeTwitterHandleLinkForAddress address={props.creator} />
            <EtherscanLinkedAddress address={props.creator} />
          </td>
        </tr>
        <tr>
          <th scope="row">Description</th>
          <td>{props.description}</td>
        </tr>
        <tr>
          <th scope="row">Drawing Address</th>
          <td><EtherscanLinkedAddress address={props.address} /></td>
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
