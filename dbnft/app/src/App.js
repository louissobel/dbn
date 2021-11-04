import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';
import { BrowserRouter, Switch, Route, Link } from "react-router-dom";


import { Web3ReactProvider } from '@web3-react/core'
import Web3 from 'web3'

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Container from 'react-bootstrap/Container';

import frontendEnvironment from './frontend_environment'
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

function App() {
  if (frontendEnvironment.environment === 'unknown') {
    console.log('unsupported environment')
    return null
  }

  return (
    <BrowserRouter>
      <Web3ReactProvider getLibrary={(p) => new Web3(p)}>
          {frontendEnvironment.config.testnetBanner &&
            <div className='dbn-testnet-banner'>
              This site is a work in progress, and
              is currently only connected to the Rinkeby testnet,
              not Ethereum mainnet.
            </div>
          }

          <Switch>
            <Route exact path="/create">
              <DBNFTNavbar active="create"/>
              <Editor />
            </Route>

            <Route exact path="/">
              <DBNFTNavbar active="about"/>
              <About />
            </Route>

            <Route path='/gallery'>
              <DBNFTNavbar active="gallery" />
              <Gallery />
            </Route>

            <Route path='/dbnft/:tokenId'>
              <DBNFTNavbar active="gallery" />
              <Viewer />
            </Route>

            <Route path='/reference'>
              <DBNFTNavbar active="reference" />
              <Reference />
            </Route>

            <Route path="*">
              {/* TODO: better 404!!!! */}
              Not Found
            </Route>
          </Switch>

      </Web3ReactProvider>
    </BrowserRouter>
  );
}

export default App;
