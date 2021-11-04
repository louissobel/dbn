import React, { useState, useEffect } from 'react';

import { useParams } from 'react-router-dom'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';

import renderDBN from '../render'
import {eth, dbnCoordinator} from '../eth_tools'
import ImageResult from '../image_result/ImageResult'
import TokenMetadataTable from '../shared/TokenMetadataTable'
import LoadingText from '../shared/LoadingText'

function Viewer() {

  const [tokenMetadata, setTokenMetadata] = useState(null);
  const [metadataLoading, setMetadataLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [rpcError, setRPCError] = useState(null);

  const [renderState, setRenderState] = useState('RENDERING');
  const [bytecode, setBytecode] = useState(null);
  const [gasUsed, setGasUsed] = useState(null);
  const [imageData, setImageData] = useState(null);

  const {tokenId} = useParams()

  const getData = async function(tokenId) {
    try {
      const tokenMetadataJSON = await dbnCoordinator
        .methods
        .tokenMetadata(tokenId)
        .call();

      var metadata = JSON.parse(tokenMetadataJSON);
    } catch (error) {
      setMetadataLoading(false)
      if (error.message.match(/UNKNOWN_ID/)) {
        setNotFound(true)
      } else {
        setRPCError(error)
      }
    }

    setTokenMetadata(metadata)
    setMetadataLoading(false)

    try {
      const bytecode = await eth.getCode(metadata.drawing_address)
      setBytecode(bytecode)

      const renderResult = await renderDBN(
        {bytecode: bytecode},
        (update, data) => {
          if (update === 'INTERPRET_PROGRESS') {
            if (data.imageData) {
              setGasUsed(data.gasUsed)
              setImageData(data.imageData)
            }
          }
        }
      )

      setRenderState('DONE')
      setGasUsed(renderResult.gasUsed)
      setImageData(renderResult.imageData)
    } catch (error) {
      // TODO: show this in the status somehow?
      console.error('error rendering: ', error)
      setRenderState('ERROR')
    }
  }

  useEffect(() => {
    getData(tokenId)
  }, [tokenId])

  function NotFound() {
    return (
      <Alert variant="warning">
        <h5>Not Found</h5>
        <p>
          No DBNFT with this ID exists
        </p>
      </Alert>
    )
  }

  function RPCError({error}) {
    return (
      <Alert variant="danger">
        <h5>Error getting token metadata</h5>
        <p>
          {error.name}: {error.message}
        </p>
      </Alert>
    )
  }

  return (
    <Container>
      <Row className="pt-3 justify-content-md-center">
        <Col sm={12} md={9} lg={8} xl={6}>
          <div class="p-3 dbn-nft-viewer">
            <h1>DBNFT #{tokenId.toString()}</h1>

            {notFound && <NotFound />}
            {rpcError && <RPCError error={rpcError} />}
            {metadataLoading && <LoadingText />}
            {tokenMetadata &&
              <>
                <ImageResult
                  description={tokenMetadata.description}

                  renderState={renderState}
                  bytecode={bytecode}
                  gasUsed={gasUsed}
                  imageData={imageData}
                />

                <TokenMetadataTable
                  tokenId={tokenId}
                  description={tokenMetadata.description}
                  address={tokenMetadata.drawing_address}
                  externalURL={tokenMetadata.external_url}
                />
              </>
            }
          </div>

        </Col>
      </Row>
    </Container>
  )
}

export default Viewer;
