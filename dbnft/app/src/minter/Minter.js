import React, {useState, useRef, useEffect} from 'react';

import { useWeb3React } from '@web3-react/core'

import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import { Icon } from '@iconify/react';


import frontendEnvironment from '../frontend_environment'
import ImageViewer from '../shared/ImageViewer'
import TokenMetadataTable from '../shared/TokenMetadataTable'
import DBNCoordinator from '../contracts/DBNCoordinator'

import {prependDeployHeader, dbnCoordinator} from '../eth_tools'
import {ipfsClient} from '../ipfs_tools'

const ALLOWLIST_FINISHED = frontendEnvironment.config.allowlistFinished;

function Minter(props) {
  const web3React = useWeb3React()

  const [contractMode, setContractMode] = useState(null)
  const [mintableTokenIds, setMintableTokenIds] = useState(null)
  const [selectedTokenId, setSelectedTokenId] = useState(null)

  const [isMinting, setIsMinting] = useState(false)
  const mintEventEmitter = useRef(null)
  const [errorMessage, setErrorMessage] = useState(null)

  const [mintResult, setMintResult] = useState(null)
  const [ipfsCID, setIPFSCID] = useState(null)
  const [mintTransactionHash, setMintTransactionHash] = useState(null)

  const [showModal, setShowModal] = useState(false)

  /* Testing minter:
   *   - Contract mode allowlistonly:
   *      - address with allowlist
   *      - address without allowlist
   *      - what happens when address mints their last one?
   *   - Contract mode Open
   *      - address with allowlist
   *      - address without allowlist
   *
   */


  function getMintabilityStatus() {
    if (mintableTokenIds === null || contractMode === null) {
      return 'PENDING'
    }

    if (contractMode === 'Open') {
      return 'MINTABLE'
    }

    // assert...
    if (contractMode !== 'AllowlistOnly') {
      throw new Error('unexpected contractMode: ' + contractMode)
    }

    if (mintableTokenIds.length > 0) {
      return 'MINTABLE'
    }

    return 'NOT_ALLOWLISTED'
  }

  const {onMintInProgress, onMintabilityStatusChange} = props;
  useEffect(() => {
    if (mintTransactionHash && mintEventEmitter.current && onMintInProgress) {
      onMintInProgress(mintTransactionHash, mintEventEmitter.current)
    }
  }, [onMintInProgress, mintTransactionHash])

  const mintability = getMintabilityStatus();
  useEffect(() => {
    if (onMintabilityStatusChange) {
      onMintabilityStatusChange(mintability)
    }
  }, [mintability, onMintabilityStatusChange])


  function getContractMode() {
    if (ALLOWLIST_FINISHED) {
      setContractMode('Open')
    } else {
      dbnCoordinator.methods.getContractMode().call()
      .then((mode) => {
        switch (mode) {
          case '0':
            setContractMode('AllowlistOnly')
            break;
          case '1':
            setContractMode('Open')
            break;
          default:
            throw new Error('unknown contract mode: ' + mode)
        }
      })
      .catch((e) => {
        console.error('error setting up mint: getting contract mode:', e)
      })
    }
  }

  useEffect(() => {
    getContractMode()
  }, [])

  useEffect(() => {
    if (web3React.account && contractMode) {
      if (ALLOWLIST_FINISHED) {
        setMintableTokenIds([])
      } else {
        dbnCoordinator.methods.getAllowedTokenIds(web3React.account).call()
        .then((allowed) => {
          setMintableTokenIds(allowed)
        })
        .catch((e) => {
          console.error('error setting up mint: getting allowed token ids:', e)
        })
      }
    } else {
      setMintableTokenIds(null)
    }
  }, [web3React.account, contractMode])


  function showMintButton() {
    if (!web3React.active) {
      return false
    }

    if (web3React.chainId !== frontendEnvironment.config.expectedChainId) {
      return false
    }

    if (mintability !== 'MINTABLE') {
      return false
    }

    return true
  }

  // if we justed minted a token, remove it from the "mintable" allowlist
  function maybeClearMintableTokenId(mintedTokenId) {
    let newTokenIds = []
    for (let id of mintableTokenIds) {
      if (id !== mintedTokenId) {
        newTokenIds.push(id)
      }
    }
    setMintableTokenIds(newTokenIds)
  }

  async function pinSourceCodeToIPFS(code) {
    try {
      setIPFSCID(await ipfsClient.pinFile(code))
    } catch (e) {
      console.error('error pinning code to IPFS!', e)
    }
  }

  async function doMint() {
    setIsMinting(true)

    const web3 = web3React.library;

    // TODO: why is this different than the gallery / viewer?
    // (I feel like I am using two different eth libraries?
    // one for reads and one for metamask??)
    const metamaskDBNCoordinator = new web3.eth.Contract(
      DBNCoordinator,
      frontendEnvironment.config.coordinatorContractAddress,
    )

    const deployBytecode = prependDeployHeader(props.bytecode)
    console.log(deployBytecode)

    let value = frontendEnvironment.config.mintPrice;
    let deployMethod = metamaskDBNCoordinator.methods.mint(deployBytecode);
    if (selectedTokenId !== null) {
      value = 0; // allowlisted minting is free
      deployMethod = metamaskDBNCoordinator.methods.mintTokenId(deployBytecode, selectedTokenId);
    }

    // TODO: how do we want to think about error handling here?
    let mintPromiEmitter = deployMethod.send({
      from: web3React.account,
      value: value,
    })
    mintEventEmitter.current = mintPromiEmitter;

    
    mintPromiEmitter
      .once('transactionHash', (h) => {
        setMintTransactionHash(h)
        pinSourceCodeToIPFS(props.code)
      })
      .then((receipt) => {
        setIsMinting(false)
        mintEventEmitter.current = null;

        setErrorMessage(null)
        maybeClearMintableTokenId(selectedTokenId)
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
    setSelectedTokenId(null);
    setMintResult(null);
    setMintTransactionHash(null)
    setErrorMessage(null);

    setIsMinting(false);
    mintEventEmitter.current = null
  }

  function renderMintResult() {
    const deployEvent = mintResult.events.DrawingDeployed;
    const transferEvent = mintResult.events.Transfer;

    const tokenId = transferEvent.returnValues.tokenId;
    const externalURL = frontendEnvironment.config.externalBase + tokenId

    return (
      <div>
        <h5>NFT Minted!</h5>
        <TokenMetadataTable
          tokenId={tokenId}
          creator={transferEvent.returnValues.to}
          description={props.description}
          address={deployEvent.returnValues.addr}
          externalURL={externalURL}
          ipfsCID={ipfsCID}
        />
      </div>
    )
  }

  function renderFooterButtons() {
    const mintDisabled = isMinting || (contractMode === 'AllowlistOnly' && !selectedTokenId)

    let mintText = "Mint"
    if (selectedTokenId) {
      mintText += ` #${selectedTokenId}`
    } else {
      // if the user _has_ the choice, make it clear this would be arbitrary
      if (contractMode === 'Open' && mintableTokenIds !== null && mintableTokenIds.length > 0) {
        mintText += " Arbitrary"
      }
    }

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

          <Button variant="warning" disabled={mintDisabled} onClick={doMint}>
            {mintText}
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

  function toggleSelectedTokenId(id) {
    if (selectedTokenId !== id) {
      setSelectedTokenId(id)
    } else {
      setSelectedTokenId(null)
    }
  }

  function tokenIdSelector() {
    if (mintableTokenIds === null || contractMode === null) {
      return null
    }

    if (mintableTokenIds.length === 0) {
      return null
    }

    let tokenIdRadios = mintableTokenIds.map((id) => {
      return <Form.Check 
        key={`token-id-${id}'`}
        type='radio'
        id={`token-id-${id}`}
        name={`token-id`}
        label={`#${id}`}
        checked={selectedTokenId === id}
        disabled={isMinting}
        onClick={() => toggleSelectedTokenId(id)}
        onChange={() => {}} // silence react warning
      />
    })

    return (
      <div className="dbn-mint-modal-tokenid-selector mt-3">
        <h6>Choose from your allowlisted token ids:</h6>

        {contractMode === 'Open' &&
          <p>
            <em>Don't select any of them to mint an arbitrary token id</em>
          </p>
        }

        {tokenIdRadios}
      </div>
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
            <div className="dbn-mint-modal-description">
              {props.description}
            </div>
          }

          {(!isMinting && !mintResult) &&
            tokenIdSelector()
          }

          <div className="dbn-mint-modal-text mt-2">
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


