import React from 'react';

import { useWeb3React } from '@web3-react/core'
import { InjectedConnector } from '@web3-react/injected-connector'

import Button from 'react-bootstrap/Button';

// TODO: set the chain IDs?
const connector = new InjectedConnector()

function ConnectorFunction(web3React) {
  return async function connect() {
    try {
     await web3React.activate(connector)
    } catch (ex) {
     console.log(ex)
    }
  }
}

function EthereumConnect() {
  const web3React = useWeb3React()
  console.log(web3React)


  async function disconnect() {
    await web3React.deactivate()
  }

  var inner;
  if (window.ethereum === undefined) {
    inner = (<>
        <div className="ethereum-connect-status error" />
        <div className = "ethereum-connect-connect-message">
          you need to install MetaMask to connect to Ethereum
        </div>

        <Button size="sm" variant="warning" href="https://metamask.io/download">
          Go to MetaMask
        </Button>
      </>
    )
  } else if (web3React.active) {
    inner = (
      <>
        <div className="ethereum-connect-status ok" />
        <div className = "ethereum-connect-connect-message">
          connected to <span style={{fontFamily: "monospace"}}>{web3React.account}</span>
        </div>

        <Button size="sm" variant="secondary" onClick={disconnect}>
          Disconnect
        </Button>
      </>
    )
  } else {
    inner = (
      <>
        <div className="ethereum-connect-status pending" />
        <div className="ethereum-connect-connect-message">
          no connected wallet
        </div>
        <Button size="sm" variant="primary" onClick={ConnectorFunction(web3React)}>
          Connect to Ethereum
        </Button>
      </>
    )
  }

  return (
    <div className="ethereum-connect-navbar" style={{color: "white"}}>
      {inner}
    </div>
  );
}
export {ConnectorFunction}
export default EthereumConnect;