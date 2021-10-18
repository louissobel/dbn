import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';

import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';

import DBNEditor from './DBNEditor'

const COMPILE_PATH = '/evm_compile'


function App() {
  return (
    <>
      <Navbar bg="dark" variant="dark">
        <Container>
          <Navbar.Brand href="#">DBNFT</Navbar.Brand>
        </Container>
      </Navbar>

      <Container>
        <DBNEditor compilePath={COMPILE_PATH}/>
      </Container>
    </>
  );
}

export default App;
