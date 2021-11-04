import React, {useState} from 'react';

import { useWeb3React } from '@web3-react/core'

import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import { Icon } from '@iconify/react';


import frontendEnvironment from '../frontend_environment'
import ImageViewer from '../shared/ImageViewer'
import TokenMetadataTable from '../shared/TokenMetadataTable'
import DBNCoordinator from '../contracts/DBNCoordinator'

import {prependDeployHeader} from '../eth_tools'


function Minter(props) {
  const web3React = useWeb3React()

  const [isMinting, setIsMinting] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)

  const [mintResult, setMintResult] = useState(null)

  const [showModal, setShowModal] = useState(false)

  function showMintButton() {
    if (!web3React.active) {
      return false
    }

    if (frontendEnvironment.config.mintWhitelist) {
      if (!frontendEnvironment.config.mintWhitelist.includes(web3React.account)) {
        return false
      }
    }

    return true
  }

  async function doMint() {
    setIsMinting(true)

    const web3 = web3React.library;

    // TODO: why is this different than the gallery??
    console.log(frontendEnvironment.config.coordinatorContractAddress)
    const dbnCoordinator = new web3.eth.Contract(
      DBNCoordinator.abi,
      frontendEnvironment.config.coordinatorContractAddress,
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
    console.log(event, mintResult)

    return (
      <div>
        <h5>NFT Minted!</h5>
        {/* TODO: I probably should get this from tokenURI...*/}

        <TokenMetadataTable
          tokenId={event.returnValues.tokenId}
          description={props.description}
          address={event.returnValues.addr}
          externalURL={event.returnValues.externalURL}
        />
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
  if (showMintButton()) {
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
          {props.description &&
            <div class="dbn-mint-modal-description">
              {props.description}
            </div>
          }

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

export default Minter;


