import React, {useState, useRef, useEffect} from 'react';

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
  const mintEventEmitter = useRef(null)
  const [errorMessage, setErrorMessage] = useState(null)

  const [mintResult, setMintResult] = useState(null)
  const [mintTransactionHash, setMintTransactionHash] = useState(null)

  const [showModal, setShowModal] = useState(false)

  const {onMintInProgress} = props;
  useEffect(() => {
    if (mintTransactionHash && mintEventEmitter.current && onMintInProgress) {
      onMintInProgress(mintTransactionHash, mintEventEmitter.current)
    }
  }, [onMintInProgress, mintTransactionHash])

  function showMintButton() {
    if (!web3React.active) {
      return false
    }

    // !! of course, this needs to be enforced at contract-level too
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
    let mintPromiEmitter = dbnCoordinator.methods.deploy(deployBytecode)
      .send({from: web3React.account})
    mintEventEmitter.current = mintPromiEmitter;

    
    mintPromiEmitter
      .once('transactionHash', (h) => {
        setMintTransactionHash(h)
      })
      .on('confirmation', (r) => console.log('confirmation', r))
      .then((receipt) => {
        setIsMinting(false)
        mintEventEmitter.current = null;

        setErrorMessage(null)
        setMintResult(receipt)
      })
      .catch((error) => {
        setIsMinting(false)
        mintEventEmitter.current = null;

        // TODO: improve this error handling?
        console.error('minting', error)
        setErrorMessage(error.message)
      })

  }

  const handleModalClose = () => setShowModal(false);
  const handleModalShow = () => {
    setShowModal(true);
    setMintResult(null);
    setMintTransactionHash(null)
    setErrorMessage(null);

    setIsMinting(false);
    mintEventEmitter.current = null
  }

  function renderMintResult() {
    const event = mintResult.events.DrawingDeployed;

    return (
      <div>
        <h5>NFT Minted!</h5>
        {/* TODO: I probably should get this from tokenURI...?*/}

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
        <Modal.Header closeButton={true}>
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

          <div class="dbn-mint-modal-text mt-2">
            {isMinting &&
              <p className="text-center">
                Minting...
              </p>
            }
            {isMinting && mintTransactionHash && 
              <p className="dbn-nft-minter-transaction-hash">
              Transaction: {mintTransactionHash}
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


