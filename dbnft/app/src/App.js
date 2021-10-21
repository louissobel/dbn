import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';

import { Web3ReactProvider } from '@web3-react/core'
import Web3 from 'web3'

import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';

import DBNEditor from './DBNEditor'
import EthereumConnect from './EthereumConnect'

const COMPILE_PATH = '/evm_compile'


function App() {
  return (
    <Web3ReactProvider getLibrary={(p) => new Web3(p)}>
      <Navbar bg="dark" variant="dark">
        <Container className="justify-content-between">
          <Navbar.Brand href="#">DBNFT</Navbar.Brand>
          <EthereumConnect />
        </Container>
      </Navbar>

      <Container>
        <DBNEditor compilePath={COMPILE_PATH}/>
      </Container>
    </Web3ReactProvider>
  );
}

export default App;
