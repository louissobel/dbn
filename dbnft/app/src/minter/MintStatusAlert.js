import React, {useState, useEffect} from 'react';

import Alert from 'react-bootstrap/Alert';
import { Link } from "react-router-dom";


function MintStatusAlert({ transactionHash, mintEventEmitter, onClose }) {
  const [mintState, setMintState] = useState('PENDING')
  const [confirmations, setConfirmations] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)
  const [tokenID, setTokenID] = useState(null)
  const [dotCount, setDotCount] = useState(1)

  useEffect(() => {
    let t = setTimeout(() => {
      setDotCount(((dotCount) % 4) + 1)
    }, 500)
    return () => {
      clearTimeout(t)
    }
  }, [dotCount])

  useEffect(() => {
    mintEventEmitter
    .on('confirmation', (n) => {
      setConfirmations(n)
    })
    .once('receipt', (r) => {
      setMintState('COMPLETE')
      setTokenID(r.events.DrawingDeployed.returnValues.tokenId)
    })
    .once('error', (e) => {
      setMintState('ERROR')
      setErrorMessage(e.message)
    })
  }, [mintEventEmitter])

  if (mintState === 'PENDING') {
    return (
      <Alert variant="warning">
        <p>
          Mint in progress{'.'.repeat(dotCount)}
        </p>

        <p className="dbn-mint-status-alert-fine-print">
          Transaction: {transactionHash}
        </p>

        {confirmations !== null && 
          <p className="dbn-mint-status-alert-fine-print">
            Confirmations: {confirmations}
          </p>
        }
      </Alert>
    )
  } else if (mintState === 'ERROR') {
    return (
        <Alert variant="danger" onClose={onClose}>
        <p>
          Error minting:
        </p>

        <p>{errorMessage}</p>

        <p className="dbn-mint-status-alert-fine-print">
          Transaction: {transactionHash}
        </p>
      </Alert>
    )
  } else if (mintState === 'COMPLETE') {
    return (
      <Alert variant="success" onClose={onClose} dismissible>
        <p>
          Successfully minted <Link to={"/dbnft/" + tokenID}>
            DBNFT #{tokenID}
          </Link>
        </p>

        {/* TODO: link this to etherscan? */}
        <p className="dbn-mint-status-alert-fine-print">
          Transaction: {transactionHash}
        </p>
      </Alert>
    )
  }
}

export default MintStatusAlert;


