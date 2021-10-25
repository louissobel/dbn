import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';
import { BrowserRouter, Switch, Route, Link } from "react-router-dom";


import { Web3ReactProvider } from '@web3-react/core'
import Web3 from 'web3'

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Container from 'react-bootstrap/Container';

import About from './About'
import DBNEditor from './DBNEditor'
import NFTViewer from './NFTViewer'
import Gallery from './Gallery'
import EthereumConnect from './EthereumConnect'

const COMPILE_PATH = '/evm_compile'

function DBNFTNavbar(props) {
  return (
    <Navbar bg="dark" variant="dark">
      <Container className="justify-content-between">
        <Navbar.Brand href="#">DBNFT</Navbar.Brand>
        <Nav className="me-auto">
          <Nav.Link as={Link} to="/" active={props.active === "about"}>About</Nav.Link>
          <Nav.Link as={Link} to="/create" active={props.active === "create"}>Create</Nav.Link>
          <Nav.Link as={Link} to="/gallery" active={props.active === "gallery"}>Gallery</Nav.Link>
        </Nav>
        <EthereumConnect />
      </Container>
    </Navbar>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Web3ReactProvider getLibrary={(p) => new Web3(p)}>


          <Switch>
            <Route exact path="/create">
              <DBNFTNavbar active="create"/>
              <DBNEditor compilePath={COMPILE_PATH}/>
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
              <NFTViewer />
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
