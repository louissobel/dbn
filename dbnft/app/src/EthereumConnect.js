import React from 'react';

import { useWeb3React } from '@web3-react/core'
import { InjectedConnector } from '@web3-react/injected-connector'

import Button from 'react-bootstrap/Button';

import StatusDot from './shared/StatusDot'

// TODO: set the chain IDs?
const connector = new InjectedConnector()

function ConnectorFunction(web3React) {
  return async function connect() {
    try {
     await web3React.activate(connector)
    } catch (ex) {
      // TODO: what about this error??
     console.log(ex)
    }
  }
}

function truncateAccount(account) {
  return account.slice(0, 5) + '...' + account.slice(38)
}


function EthereumConnect() {
  const web3React = useWeb3React()

  async function disconnect() {
    await web3React.deactivate()
  }

  var inner;
  if (window.ethereum === undefined) {
    inner = (<>
        <StatusDot error />
        <div className = "d-none d-lg-inline-block ethereum-connect-connect-message">
          you need to install MetaMask to connect to Ethereum
        </div>
        <div className = "d-none d-md-inline-block d-lg-none ethereum-connect-connect-message">
          MetaMask not installed
        </div>


        <Button size="sm" variant="warning" href="https://metamask.io/download">
          Go to MetaMask
        </Button>
      </>
    )
  } else if (web3React.active) {
    inner = (
      <>
        <StatusDot ok />
        <div className = "d-none d-lg-inline-block ethereum-connect-connect-message">
          connected to <span style={{fontFamily: "monospace"}}>{web3React.account}</span>
        </div>
        <div className = "d-none d-md-inline-block d-lg-none ethereum-connect-connect-message">
          connected to <span style={{fontFamily: "monospace"}}>{truncateAccount(web3React.account)}</span>
        </div>

        <Button size="sm" variant="secondary" onClick={disconnect}>
          Disconnect
        </Button>
      </>
    )
  } else {
    inner = (
      <>
        <StatusDot pending />
        <div className="d-none d-md-inline-block ethereum-connect-connect-message">
          not connected to ethereum
        </div>
        <Button size="sm" variant="primary" onClick={ConnectorFunction(web3React)}>
          Connect
        </Button>
      </>
    )
  }

  return (
    <div className="d-none d-sm-inline-block ethereum-connect-navbar" style={{color: "white"}}>
      {inner}
    </div>
  );
}
export {ConnectorFunction}
export default EthereumConnect;
