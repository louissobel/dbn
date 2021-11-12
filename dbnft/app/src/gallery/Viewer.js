import React, { useState, useEffect } from 'react';

import { useParams } from 'react-router-dom'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';
import { binary_to_base58 } from 'base58-js'

import frontendEnvironment from '../frontend_environment'
import renderDBN from '../render'
import {eth, dbnCoordinator} from '../eth_tools'
import {ipfsClient} from '../ipfs_tools'
import ImageResult from '../image_result/ImageResult'
import TokenMetadataTable from '../shared/TokenMetadataTable'
import LoadingText from '../shared/LoadingText'

import CodeMirror from '@uiw/react-codemirror';
import {lineNumbers} from "@codemirror/gutter"
import {dbnLanguage, dbnftHighlightStyle} from '../lang-dbn/dbn'

function Viewer() {

  const [tokenMetadata, setTokenMetadata] = useState(null);
  const [creator, setCreator] = useState(null);
  const [metadataLoading, setMetadataLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [rpcError, setRPCError] = useState(null);

  const [renderState, setRenderState] = useState('RENDERING');
  const [bytecode, setBytecode] = useState(null);
  const [gasUsed, setGasUsed] = useState(null);
  const [imageData, setImageData] = useState(null);

  const [ipfsCID, setIPFSCID] = useState(null)
  const [sourceCode, setSourceCode] = useState(null);

  const {tokenId} = useParams()

  const getData = async function(tokenId) {
    try {
      const tokenMetadataJSON = await dbnCoordinator
        .methods
        .tokenMetadata(tokenId)
        .call();

      var metadata = JSON.parse(tokenMetadataJSON);

      const creationEvents = await dbnCoordinator
        .getPastEvents('Transfer', {
          fromBlock: 0,
          toBlock: 'latest',
          filter: {
            from: 0,
            tokenId: tokenId,
          }
        })

      if (creationEvents.length !== 1) {
        console.warn('unexpected number of creationEvent: ' + creationEvents.length)
      } else {
        const creationEvent = creationEvents[0]
        setCreator(creationEvent.returnValues.to)
      }
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
        {bytecode: bytecode, codeAddress: metadata.drawing_address},
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

  useEffect(() => {
    if (bytecode) {
      // This... is a big assumption, but going to prefer it
      // over adding another RPC to the draw harness
      let ipfsHash = Buffer.from(bytecode.slice(
        bytecode.length - 64,
        bytecode.length,
      ), 'hex')

      let cid = binary_to_base58(Buffer.concat([
        Buffer.from([0x12, 0x20]),
        ipfsHash,
      ]))

      setIPFSCID(cid)
    }
  }, [bytecode])


  async function getCodeFromIPFS(cid) {
    try {
      const code = await ipfsClient.getTextFile(cid)
      setSourceCode(code)
    } catch (e) {
      console.error('failed to get code from IPFS: ', e)
    }
  }

  useEffect(() => {
    if (ipfsCID) {
      getCodeFromIPFS(ipfsCID)
    }
  }, [ipfsCID])

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

  const openSeaURL = (
    frontendEnvironment.config.openSeaBase +
    "/assets/" +
    frontendEnvironment.config.coordinatorContractAddress +
    "/" + 
    tokenId
  );

  return (
    <Container>
      <Row className="pt-3 justify-content-md-center">
        <Col sm={12} md={9} lg={8} xl={6}>
          <div className="dbn-nft-viewer">
            <h1>DBNFT #{tokenId.toString()}</h1>

            {notFound && <NotFound />}
            {rpcError && <RPCError error={rpcError} />}
            {metadataLoading && <LoadingText />}
            {tokenMetadata &&
              <>
                <div className="dbn-nft-viewer-opensea">
                  <a href={openSeaURL}>View on OpenSea</a>
                </div>

                <ImageResult
                  description={tokenMetadata.description}

                  renderState={renderState}
                  bytecode={bytecode}
                  gasUsed={gasUsed}
                  imageData={imageData}
                />

                <TokenMetadataTable
                  tokenId={tokenId}
                  creator={creator}
                  description={tokenMetadata.description}
                  address={tokenMetadata.drawing_address}
                  externalURL={tokenMetadata.external_url}
                  // ipfsCID={ipfsCID}
                />

                {sourceCode &&
                  <div className="dbn-nft-viewer-source mt-4">
                    <h5>Source Code</h5>
                    {ipfsCID &&
                      <p className="dbn-nft-viewer-ipfs-url">ipfs://{ipfsCID}</p>
                    }
                    <div className="dbn-readonly-code-wrapper">
                      <CodeMirror
                        value={sourceCode}
                        extensions={[
                          lineNumbers(),
                          dbnLanguage,
                          dbnftHighlightStyle,
                        ]}
                        autoFocus={false}
                        editable={false}
                        basicSetup={false}
                      />
                    </div>
                  </div>
                }

              </>
            }
          </div>

        </Col>
      </Row>
    </Container>
  )
}

export default Viewer;
