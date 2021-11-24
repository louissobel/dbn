import React, { useState, useEffect, useCallback } from 'react';

import { useWeb3React } from '@web3-react/core'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Form from 'react-bootstrap/Form';

import frontendEnvironment from './frontend_environment'
import {Ticket} from './allowlist'
import {dbnCoordinator, modeStringForContractMode} from './eth_tools'
import DBNCoordinator from './contracts/DBNCoordinator'
import LoadingText from './shared/LoadingText'


function getMetamaskDBNCoordinator(web3) {
  return new web3.eth.Contract(
    DBNCoordinator,
    frontendEnvironment.config.coordinatorContractAddress,
  )
}

function Signer() {
  const [tokenId, setTokenId] = useState("")
  const [minter, setMinter] = useState("")

  const [signing, setSigning] = useState(false)
  const [ticketText, setTicketText] = useState(null)
  const [signatureError, setSignatureError] = useState(null)

  const web3React = useWeb3React()
  const web3 = web3React.library;

  const doSign = useCallback((tokenId, minter) => {
    setSigning(true)
    setTicketText(null)
    setSignatureError(null)

    Ticket.generate(web3, web3React.account, {
      tokenId: tokenId,
      minter: minter,
      coordinator: frontendEnvironment.config.coordinatorContractAddress,
      ticketId: web3.utils.randomHex(32),
    })
    .then((ticket) => {
      setTicketText(ticket.serialize())
      setSigning(false)
    })
    .catch((e) => {
      setSignatureError(e)
      setSigning(false)
    })
  }, [web3React.account, web3])

  return (
    <>
      <Form className="mb-3">
        <Row>
          <Col xs="2">
            <Form.Label>Token ID</Form.Label>
          </Col>

          <Col xs="2">
            <Form.Control
              type="text"
              value={tokenId}
              onChange={(e) => setTokenId(e.target.value)}
            />
          </Col>
        </Row>

        <Row className="mt-1">
          <Col xs="2">
            <Form.Label>Minter</Form.Label>
          </Col>

          <Col>
            <Form.Control
              type="text"
              value={minter}
              onChange={(e) => setMinter(e.target.value)}
            />
          </Col>
        </Row>
      </Form>

      <Button
        className="mb-2"
        variant="primary"
        onClick={() => doSign(tokenId, minter)}
        disabled={signing}
      >
        Sign
      </Button>

      <p>Ticket:</p>
      {signatureError && 
        <Alert variant="danger">{signatureError.message}</Alert>
      }
      <pre className="mt-3 dbn-low-level-code wordwrap">{ticketText}</pre>
    </>
  )
}

function Opener({ onOpen }) {
  const [opening, setOpening] = useState(false)
  const [error, setError] = useState(null)

  const web3React = useWeb3React()
  const web3 = web3React.library;
  const metamaskDBNCoordinator = getMetamaskDBNCoordinator(web3)

  function doOpen() {
    setOpening(true)

    metamaskDBNCoordinator.methods.openMinting().send({
      from: web3React.account,
    })
    .then(() => {
      onOpen()
    })
    .catch((e) => {
      setError(e)
      setOpening(false)
    })
  }

  return (
    <>
      <Button
        variant="warning"
        onClick={doOpen}
        disabled={opening}
      >
        Open Contract
      </Button>

      {error &&
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          {error.message}
        </Alert>
      }
    </>

  )
}

function MintPriceUpdater({ onMintPriceUpdate }) {
  const [updating, setUpdating] = useState(false)
  const [error, setError] = useState(null)
  const [input, setInput] = useState("")
  const [inputAsEth, setInputAsEth] = useState(null)
  const [invalidInput, setInvalidInput] = useState(false)

  const web3React = useWeb3React()
  const web3 = web3React.library;
  const metamaskDBNCoordinator = getMetamaskDBNCoordinator(web3)

  function handleInputChange(e) {
    const nextInput = e.target.value;

    setInput(nextInput)

    if (nextInput === "") {
      setInvalidInput(false)
      setInputAsEth(null)
    } else {
      let formatted;
      try {
        formatted = maybeFormatWei(web3, nextInput)
      } catch (e) {
        setInvalidInput(true)
        setInputAsEth(null)
        return;
      }

      setInputAsEth(formatted)
      setInvalidInput(false)
    }
  }

  function doUpdate() {
    setUpdating(true)
    setError(null)

    let result;
    try {
      result = metamaskDBNCoordinator.methods.setMintPrice(input).send({
        from: web3React.account,
      })
    } catch (e) {
      setError(e);
      setUpdating(false);
      return;
    }

    result.then(() => {
      onMintPriceUpdate(input)
      setUpdating(false)
      setInput("")
      setInputAsEth(null)
    })
    .catch((e) => {
      setError(e)
      setUpdating(false)
    })
  }

  return (
    <Col sm="9">
      <InputGroup size="sm" className="mb-2">
        <InputGroup.Text>
          {inputAsEth}
        </InputGroup.Text>
        <FormControl
          className={invalidInput ? "border-danger" : ""}
          placeholder="(in wei)"
          value={input}
          onChange={handleInputChange}
        />
        <Button
          variant="warning"
          onClick={doUpdate}
          disabled={updating}
        >
          Update
        </Button>
      </InputGroup>

      {error &&
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          {error.message}
        </Alert>
      }
    </Col>
  )
}

function Withdrawer({ onWithdraw }) {
  const [withdrawing, setWithdrawing] = useState(false)
  const [error, setError] = useState(null)

  const web3React = useWeb3React()
  const web3 = web3React.library;
  const metamaskDBNCoordinator = getMetamaskDBNCoordinator(web3)

  function doWithdraw() {
    setWithdrawing(true)

    metamaskDBNCoordinator.methods.withdraw().send({
      from: web3React.account,
    })
    .then(() => {
      onWithdraw()
      setWithdrawing(false)
    })
    .catch((e) => {
      setError(e)
      setWithdrawing(false)
    })
  }

  return (
    <>
      <Button
        className="ms-3"
        size="sm"
        variant="success"
        onClick={doWithdraw}
        disabled={withdrawing}
      >
        Withdraw
      </Button>
      {error &&
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          {error.message}
        </Alert>
      }
    </>
  )
}

function maybeFormatWei(web3, v) {
  if (v === null) {
    return null
  }

  return "Ξ" + web3.utils.fromWei(v)
}


function Admin() {
  const [contractMode, setContractMode] = useState(null)
  const [totalSupply, setTotalSupply] = useState(null)
  const [mintPrice, setMintPrice] = useState(null)
  const [balance, setBalance] = useState(null)

  const web3React = useWeb3React()
  const web3 = web3React.library;

  async function loadContractMode() {
    const mode = await dbnCoordinator.methods.getContractMode().call();
    setContractMode(modeStringForContractMode(mode))
  }

  async function loadTotalSupply() {
    setTotalSupply(await dbnCoordinator.methods.totalSupply().call());
  }

  async function loadMintPrice() {
    setMintPrice(await dbnCoordinator.methods.getMintPrice().call())
  }

  async function loadBalance() {
    setBalance(await web3.eth.getBalance(frontendEnvironment.config.coordinatorContractAddress))
  }

  useEffect(() => {
    if (web3React.active) {
      loadContractMode()
      loadTotalSupply()
      loadMintPrice()
      loadBalance()
    }
  }, [web3React.active])

  function loadingIfNull(v) {
    if (v === null) {
      return <LoadingText />
    } else {
      return v
    }
  }

  function content() {
    if (!web3React.active) {
      return (
        <Alert variant="warning" >
          Not connected to metamask
        </Alert>
      )
    }

    if (web3React.account !== frontendEnvironment.config.coordinatorOwner) {
      return (
        <Alert variant="warning" >
          Not owner
        </Alert>
      )
    }

    return (
      <>
        <h3>Config</h3>

        <table className="table border-dark">
          <tbody>
            <tr>
              <th scope="row">Chain ID</th>
              <td><code>{web3React.chainId}</code></td>
            </tr>

            <tr>
              <th scope="row">Coordinator</th>
              <td><code>{frontendEnvironment.config.coordinatorContractAddress}</code></td>
            </tr>

            <tr>
              <th scope="row">Contract Mode</th>
              <td><code>{loadingIfNull(contractMode)}</code></td>
            </tr>

            <tr>
              <th scope="row">Minted Tokens</th>
              <td><code>{loadingIfNull(totalSupply)}</code></td>
            </tr>

            <tr>
              <th scope="row">Mint Price</th>
              <td>
                <code>{loadingIfNull(maybeFormatWei(web3, mintPrice))}</code>
                <MintPriceUpdater onMintPriceUpdate={setMintPrice} />
              </td>
            </tr>

            <tr>
              <th scope="row">Balance</th>
              <td>
                <code>{loadingIfNull(maybeFormatWei(web3, balance))}</code>
                <Withdrawer onWithdraw={() => setBalance('0')} />
              </td>
            </tr>
          </tbody>
        </table>

        {contractMode !== 'Open' &&
          <Opener onOpen={() => setContractMode('Open')} />
        }


        <h3 className="mt-5">Signing</h3>
        <Signer />

      </>

    )
  }

  return (
    <Container>
      <Row className="pt-3">
        <Col sm="9">
          {content()}
        </Col>
      </Row>
    </Container>
  )
}

export default Admin;