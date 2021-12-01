import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';
import { ErrorBoundary } from '@rollbar/react'
import {Helmet} from "react-helmet";
import { BrowserRouter, Switch, Route, Link } from "react-router-dom";
import { Provider as RollbarProvider } from '@rollbar/react'

import { Web3ReactProvider, useWeb3React } from '@web3-react/core'
import Web3 from 'web3'

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Container from 'react-bootstrap/Container';

import frontendEnvironment from './frontend_environment'
import Admin from './Admin'
import About from './site/About'
import Editor from './editor/Editor'
import Viewer from './gallery/Viewer'
import Gallery from './gallery/Gallery'
import Reference from './site/Reference'
import EthereumConnect from './EthereumConnect'

function DBNFTNavbar(props) {
  return (
    <Navbar bg="dark" variant="dark">
      <Container className="justify-content-between">
        <Navbar.Brand href="#">DBNFT</Navbar.Brand>
        <Nav className="me-auto">
          <Nav.Link as={Link} to="/" active={props.active === "about"}>About</Nav.Link>
          <Nav.Link as={Link} to="/create" active={props.active === "create"}>Create</Nav.Link>
          <Nav.Link as={Link} to="/gallery" active={props.active === "gallery"}>Gallery</Nav.Link>
          <Nav.Link as={Link} to="/reference" active={props.active === "reference"}>Reference</Nav.Link>
        </Nav>
        <EthereumConnect />
      </Container>
    </Navbar>
  )
}

function WrongEthereumNetworkWarning() {
  const web3React = useWeb3React()

  if (!web3React.chainId) {
    return null
  }

  if (web3React.chainId === frontendEnvironment.config.expectedChainId) {
    return null
  }

  function messageForChainId(chainId) {
    switch(chainId) {
      case 1:
        return (<p>Access the mainnet instance at <a className="text-light" href="https://dbnft.io">dbnft.io</a></p>)
      case 4:
        return (<p>Access the Rinkeby instance at <a className="text-light" href="https://testnet.dbnft.io">testnet.dbnft.io</a></p>)
      case 5777:
        return (<p>Are you still connected to localhost?</p>)
      default:
        return (<p>This site supports only Rinkeby and mainnet</p>)
    }
  }

  return (
    <div className="dbn-wrong-chain">
      <p>
        Your metamask is currently connected to a different chain ({web3React.chainId}) than expected.
      </p>

      {messageForChainId(web3React.chainId)}
    </div>
  )
}

function UnhandledError() {
  return (
    <div className="dbn-top-level-unexpected-error">
      Unexpected error. This has been logged, but in the meantime
      try refreshing the page. Sorry!
    </div>
  )
}


function App() {
  if (frontendEnvironment.environment === 'unknown') {
    console.log('unsupported environment')
    return null
  }

  const rollbarConfig = {
    accessToken: frontendEnvironment.config.rollbarAccessToken,
    environment: frontendEnvironment.environment,
  };

  return (
    <RollbarProvider config={rollbarConfig}>
    <BrowserRouter>
      <Helmet>
        <title>DBNFT</title>
      </Helmet>

      <Web3ReactProvider getLibrary={(p) => new Web3(p)}>
        <ErrorBoundary fallbackUI={UnhandledError}>

          {frontendEnvironment.config.testnetBanner &&
            <div className='dbn-testnet-banner'>
              This site is a work in progress, and
              is currently only connected to the Rinkeby testnet,
              not Ethereum mainnet.
            </div>
          }

          <Switch>
            <Route exact path="/create">
              <Helmet>
                <title>DBNFT — Create</title>
              </Helmet>
              <DBNFTNavbar active="create"/>
              <WrongEthereumNetworkWarning />
              <Editor />
            </Route>

            <Route exact path="/">
              <DBNFTNavbar active="about"/>
              <About />
            </Route>

            <Route path='/gallery'>
              <Helmet>
                <title>DBNFT — Gallery</title>
              </Helmet>
              <DBNFTNavbar active="gallery" />
              <Gallery />
            </Route>

            <Route path='/dbnft/:tokenId'>
              <DBNFTNavbar active="gallery" />
              <Viewer />
            </Route>

            <Route path='/reference'>
              <Helmet>
                <title>DBNFT — Reference</title>
              </Helmet>
              <DBNFTNavbar active="reference" />
              <Reference />
            </Route>

            <Route path='/admin'>
              <DBNFTNavbar active="" />
              <WrongEthereumNetworkWarning />
              <Admin />
            </Route>

            <Route path="*">
              <div className="dbn-top-level-unexpected-error">
                URL not found!
              </div>
            </Route>
          </Switch>

        </ErrorBoundary>
      </Web3ReactProvider>
    </BrowserRouter>
    </RollbarProvider>
  );
}

export default App;
