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
import {Ticket, getAllowlistHints} from './allowlist'
import {dbnCoordinator, modeStringForContractMode} from './eth_tools'
import DBNCoordinator from './contracts/DBNCoordinator'
import LoadingText from './shared/LoadingText'


function getMetamaskDBNCoordinator(web3) {
  return new web3.eth.Contract(
    DBNCoordinator,
    frontendEnvironment.config.coordinatorContractAddress,
  )
}

function Address({value}) {
  const link = frontendEnvironment.config.etherscanBase + "/address/" + value;
  return <a href={link}><code>{value}</code></a>
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
        variant="danger"
        onClick={doOpen}
        size="sm"
        className="ms-3"
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
        formatted = formatWei(web3, nextInput)
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

function RecipientSetter({ onRecipientUpdate }) {
  const [updating, setUpdating] = useState(false)
  const [error, setError] = useState(null)
  const [input, setInput] = useState("")

  const web3React = useWeb3React()
  const web3 = web3React.library;
  const metamaskDBNCoordinator = getMetamaskDBNCoordinator(web3)

  function handleInputChange(e) {
    setInput(e.target.value)
  }

  function doUpdate() {
    setUpdating(true)
    setError(null)

    let result;
    try {
      result = metamaskDBNCoordinator.methods.setRecipient(input).send({
        from: web3React.account,
      })
    } catch (e) {
      setError(e);
      setUpdating(false);
      return;
    }

    result.then(() => {
      onRecipientUpdate(input)
      setUpdating(false)
      setInput("")
    })
    .catch((e) => {
      setError(e)
      setUpdating(false)
    })
  }

  return (
    <Col>
      <InputGroup size="sm" className="mb-2">
        <FormControl
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

function RecipientLocker({ onRecipientLocked }) {
  const [locking, setLocking] = useState(false)
  const [error, setError] = useState(null)

  const web3React = useWeb3React()
  const web3 = web3React.library;
  const metamaskDBNCoordinator = getMetamaskDBNCoordinator(web3)

  function doLock() {
    setLocking(true)

    metamaskDBNCoordinator.methods.lockRecipient().send({
      from: web3React.account,
    })
    .then(() => {
      onRecipientLocked()
    })
    .catch((e) => {
      setError(e)
      setLocking(false)
    })
  }

  return (
    <>
      <Button
        variant="danger"
        className="ms-3"
        onClick={doLock}
        size="sm"
        disabled={locking}
      >
        Lock
      </Button>

      {error &&
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          {error.message}
        </Alert>
      }
    </>

  )
}


function Disburser({ onDisburse }) {
  const [disbursing, setDisbursing] = useState(false)
  const [error, setError] = useState(null)

  const web3React = useWeb3React()
  const web3 = web3React.library;
  const metamaskDBNCoordinator = getMetamaskDBNCoordinator(web3)

  function doDisburse() {
    setDisbursing(true)

    metamaskDBNCoordinator.methods.disburse().send({
      from: web3React.account,
    })
    .then(() => {
      onDisburse()
      setDisbursing(false)
    })
    .catch((e) => {
      setError(e)
      setDisbursing(false)
    })
  }

  return (
    <>
      <Button
        className="ms-3"
        size="sm"
        variant="success"
        onClick={doDisburse}
        disabled={disbursing}
      >
        Disburse
      </Button>
      {error &&
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          {error.message}
        </Alert>
      }
    </>
  )
}

function formatWei(web3, v) {
  return "Ξ" + web3.utils.fromWei(v)
}

function AllowlistHints({ data }) {
  let rows = []
  for (let e of Object.entries(data)) {
    rows.push(
      <tr><td>{e[0]}</td><td><Address value={e[1]} /></td></tr>
    )
  }

  return (
    <table className="mb-5 table border-dark">
      <thead>
        <tr>
          <td>Token ID</td>
          <td>Minter</td>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  )
}


function Admin() {
  const [contractMode, setContractMode] = useState(null)
  const [totalSupply, setTotalSupply] = useState(null)
  const [mintPrice, setMintPrice] = useState(null)
  const [recipient, setRecipient] = useState(null)
  const [recipientLocked, setRecipientLocked] = useState(null)
  const [balance, setBalance] = useState(null)

  const [allowlistHints, setAllowlistHints] = useState(null)

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

  async function loadRecipient() {
    setRecipient(await dbnCoordinator.methods.recipient().call());
  }

  async function loadRecipientLocked() {
    setRecipientLocked(await dbnCoordinator.methods.recipientLocked().call());
  }

  async function loadBalance() {
    setBalance(await web3.eth.getBalance(frontendEnvironment.config.coordinatorContractAddress))
  }

  async function loadAllowlistHints() {
    setAllowlistHints(await getAllowlistHints())
  }

  useEffect(() => {
    if (web3React.active) {
      loadContractMode()
      loadTotalSupply()
      loadMintPrice()
      loadRecipient()
      loadRecipientLocked()
      loadBalance()
      loadAllowlistHints()
    }
  }, [web3React.active])

  function loadingIfNull(v, f) {
    if (v === null) {
      return <LoadingText />
    } else {
      if (f === undefined) {
        return v
      } else {
        return f(v)
      }
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
              <td>
                <Address value={frontendEnvironment.config.coordinatorContractAddress} />
              </td>
            </tr>

            <tr>
              <th scope="row">Contract Mode</th>
              <td>
                <code>{loadingIfNull(contractMode)}</code>
                {contractMode !== 'Open' &&
                  <Opener onOpen={() => setContractMode('Open')} />
                }
              </td>
            </tr>

            <tr>
              <th scope="row">Minted Tokens</th>
              <td><code>{loadingIfNull(totalSupply)}</code></td>
            </tr>

            <tr>
              <th scope="row">Mint Price</th>
              <td>
                <code>{loadingIfNull(mintPrice, (p) => formatWei(web3, mintPrice))}</code>
                <MintPriceUpdater onMintPriceUpdate={setMintPrice} />
              </td>
            </tr>

            <tr>
              <th scope="row">Recipient</th>
              <td>
                {loadingIfNull(recipient, (r) => <Address value={r} />)}
                {!recipientLocked &&
                  <RecipientSetter onRecipientUpdate={setRecipient} />
                }
              </td>
            </tr>

            <tr>
              <th scope="row">Recipient Locked</th>
              <td>
                <code>{loadingIfNull(recipientLocked === null ? recipientLocked : recipientLocked.toString())}</code>
                {!recipientLocked && 
                  <RecipientLocker onRecipientLocked={() => setRecipientLocked(true)} />
                }
              </td>
            </tr>

            <tr>
              <th scope="row">Balance</th>
              <td>
                <code>{loadingIfNull(balance, (b) => formatWei(web3, b))}</code>
                <Disburser onDisburse={() => setBalance('0')} />
              </td>
            </tr>
          </tbody>
        </table>

        <h3 className="mt-5">Signing</h3>
        <Signer />

        <h3 className="mt-5">Allowlist Hints</h3>
        {allowlistHints === null && <LoadingText />}
        {allowlistHints && <AllowlistHints data={allowlistHints} />}

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
