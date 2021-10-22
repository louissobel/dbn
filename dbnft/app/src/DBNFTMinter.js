import React, {useState} from 'react';

import { useWeb3React } from '@web3-react/core'

import Accordion from 'react-bootstrap/Accordion';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import { Icon } from '@iconify/react';


import {ConnectorFunction} from './EthereumConnect'
import ImageViewer from './ImageViewer'
import DBNCoordinator from './contracts/DBNCoordinator'
import {prependDeployHeader} from './evm_tools'

function DBNFTMinter(props) {
  const web3React = useWeb3React()

  const [isMinting, setIsMinting] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [mintResult, setMintResult] = useState(null)

  const [showModal, setShowModal] = useState(false)

  async function doMint() {
    setIsMinting(true)

    const web3 = web3React.library;
    const dbnCoordinator = new web3.eth.Contract(
      DBNCoordinator.abi,
      '0x4D3d514D70DBA42Ab66F9F9115D3d028E5306368'
    )

    const deployBytecode = prependDeployHeader(props.bytecode)
    console.log(deployBytecode)

    // TODO: how do we want to think about error handling here?
     dbnCoordinator.methods.deploy(deployBytecode)
      .send({from: web3React.account})
      .then((result) => {
        setIsMinting(false)
        setErrorMessage(null)
        setMintResult(result)
        console.log(result)
      })
      .catch((error) => {
        setIsMinting(false)

        // TODO: improve this error handling?
        console.log(error)
        setErrorMessage(error.message)
      })

  }

  const handleModalClose = () => setShowModal(false);
  const handleModalShow = () => {
    setShowModal(true);
    setMintResult(null);
    setErrorMessage(null);
    setIsMinting(false);
  }

  function renderMintResult() {
    const event = mintResult.events.DrawingDeployed;

    return (
      <div>
        <h5>NFT Minted!</h5>

        <table className="table dbn-mint-success-table">
          <tbody>
            <tr>
              <th scope="row">Token ID</th>
              <td>
                {event.returnValues.addr}
              </td>
            </tr>
            <tr>
              <th scope="row">Serial #</th>
              <td>....</td>
            </tr>
            <tr>
              <th scope="row">Name</th>
              <td>....</td>
            </tr>
            <tr>
              <th scope="row">Description</th>
              <td>....</td>
            </tr>
            <tr>
              <th scope="row">URL</th>
              <td>....</td>
            </tr>
          </tbody>
        </table>

      </div>
    )
  }

  function renderFooterButtons() {
    if (mintResult) {
      return (
        <Button variant="success" onClick={handleModalClose}>
          Close
        </Button>
      )
    } else {
      return (
        <>
          <Button variant="secondary" disabled={isMinting} onClick={handleModalClose}>
            Cancel
          </Button>

          <Button variant="warning" disabled={isMinting} onClick={doMint}>
            Mint
          </Button>
        </>
      )
    }
  }

  var mintButton;
  if (web3React.active) {
    mintButton = (
      <Button variant="warning" disabled={props.disabled} onClick={handleModalShow}>Mint</Button>
    )
  }

  return (
    <>
      <div className = "d-grid">
        {mintButton}
      </div>

      <Modal
        show={showModal}
        onHide={handleModalClose}
        backdrop={isMinting ? "static" : true}
        keyboard={!isMinting}
        className="dbn-mint-modal"
      >
        <Modal.Header closeButton={!isMinting}>
          <Modal.Title>
            Mint DBN NFT
            <Icon icon="mdi:ethereum" inline={true} />
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ImageViewer
            imageData={props.imageData}
            magnify={1}
            extraClass="mx-auto"
          />

          <div class="dbn-mint-modal-text">
            {isMinting &&
              <p>
                Minting...
              </p>
            }

            {errorMessage &&
              <Alert variant="danger">
                {errorMessage}
              </Alert>
            }

            {mintResult &&
              renderMintResult()
            }
          </div>
        </Modal.Body>

        <Modal.Footer>
          {renderFooterButtons()}
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default DBNFTMinter;


