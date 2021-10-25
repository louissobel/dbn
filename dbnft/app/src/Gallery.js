import React, { useState, useEffect, useLayoutEffect, useCallback } from 'react';

import { useHistory } from "react-router-dom";
import { useWeb3React } from '@web3-react/core'
import { Icon } from '@iconify/react'
import { AutoSizer, List, WindowScroller } from 'react-virtualized'


import DBNCoordinator from './contracts/DBNCoordinator'
import Eth  from 'web3-eth';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';

import renderDBN from './dbn_renderer'
import LoadingText from './LoadingText'
import ImageViewer from './ImageViewer'


const eth = new Eth('http://localhost:8545')

const dbnCoordinator = new eth.Contract(
  DBNCoordinator.abi,
  process.env.REACT_APP_DBN_COORDINATOR_CONTRACT_ADDRESS,
)

const renderJobCache = {}


class RenderJob {
  constructor(tokenId) {
    this.tokenId = tokenId;
    this.renderState = 'INITIAL';

    this.onNewImage = null
    this.onRenderStateChange = null
  }

  async run() {
    this._setRenderState('LOADING_BYTECODE')

    // TODO: error handling!
    const bytecode = await dbnCoordinator.methods.tokenCode(this.tokenId).call()

    this._setRenderState('INTERPRETING')

    // TODO: ERROR HANDLING!!!
    const renderResult = await renderDBN(
      {bytecode: bytecode},
      (update, data) => {
        if (update === 'INTERPRET_PROGRESS') {
          if (data.imageData) {
            this._newImage(data.imageData)
          }
        }
      }
    )

    this.result = renderResult;
    this._newImage(renderResult.imageData)
    this._setRenderState('DONE')
  }

  _setRenderState(newState) {
    this.renderState = newState;
    if (this.onRenderStateChange) {
      this.onRenderStateChange(newState)
    }
  }

  _newImage(data) {
    if (this.onNewImage) {
      this.onNewImage(data)
    }
  }
}



function Item({ id, present }) {
  const [renderState, setRenderState] = useState(null)
  const [imageData, setImageData] = useState(null)

  const history = useHistory();

  useEffect(() => {
    if (!present) {
      return;
    }

    let renderJob = renderJobCache[id]
    if (renderJob) {
      if (renderJob.renderState === 'DONE') {
        // then great, use the data
        setImageData(renderJob.result.imageData)
        setRenderState('DONE')
      } else {
        // reattach this element as the listener
        renderJob.onRenderStateChange = setRenderState
        renderJob.onNewImage = setImageData
        setRenderState(renderJob.renderState)        
      }

    } else {
      // create and start new job
      renderJob = new RenderJob(id)
      renderJobCache[id] = renderJob

      renderJob.onRenderStateChange = setRenderState
      renderJob.onNewImage = setImageData

      renderJob.run()
    }

    return function() {
      // detach from the render job
      renderJob.onRenderStateChange = null
      renderJob.onNewImage = null
    }

  }, [present])


  function goToDetail() {
    history.push("/dbnft/" + id)
  }

  return (
    <div key={id} class="dbn-nft-gallery-item">
       #{id}

        {(renderState === 'INTERPRETING' || renderState === 'DONE') &&
          <ImageViewer onClick={goToDetail} imageData={imageData} magnify={1}/>
        }

       {(renderState === 'LOADING_BYTECODE' || renderState === 'INTERPRETING') &&
         <div class="dbn-nft-gallery-item-loader">
           <Icon icon="mdi:ethereum" inline={true} />
         </div>
        }
    </div>
  )
}

function Gallery() {
  const [loading, setLoading] = useState(true)
  const [rpcError, setRPCError] = useState(null)
  const [presentTokens, setPresentTokens] = useState(null)

  useEffect(async () => {
    // TODO: handle errors!?
    const totalSupply = await dbnCoordinator.methods.totalSupply().call()
    const newPresentTokens = {};

    // TOOD: this probably needs to be cached
    // in some way or another... or maybe I have a
    // call in the coordinator itself that returns it?
    for (var i=0;i<totalSupply;i++) {
      let tokenId = await dbnCoordinator.methods.tokenByIndex(i).call()
      newPresentTokens[tokenId] = true
    }
    setPresentTokens(newPresentTokens)
    setLoading(false)
  }, [])

  function makeList() {
    return (
      <div class="dbn-nft-gallery-items-holder">
        <WindowScroller>
          {({ height, isScrolling, onChildScroll, scrollTop }) => (
            <AutoSizer disableHeight>
              {({ width }) => {
                const itemWidth = 101 + 20; // (width and margins)
                const itemHeight = 101 + 20;
                const totalNumber = 101 * 101;
                const itemsPerRow = Math.max(Math.floor(width / itemWidth), 1);
                const rowCount = Math.ceil(totalNumber / itemsPerRow);

                function renderRow({ index, key, style }) {
                  const items = [];
                  const convertedIndex = index * itemsPerRow;

                  for (let i = convertedIndex; i < convertedIndex + itemsPerRow && i<totalNumber; i++) {
                    items.push(
                      <Item key={i} id={i} present={!!presentTokens[i]}/>
                    )
                  }

                  return (
                    <div
                      className='Row'
                      key={key}
                      style={style}
                    >
                      {items}
                    </div>
                  )
                }

                return (
                  <List
                    className='List'
                    width={width}
                    autoHeight
                    height={height}
                    isScrolling={isScrolling}
                    onScroll={onChildScroll}
                    scrollTop={scrollTop}
                    rowCount={rowCount}
                    rowHeight={itemHeight}
                    rowRenderer={renderRow}
                  />
                )
              }}
            </AutoSizer>
          )}
        </WindowScroller>
      </div>
    )
  }

  return (
    <div class="pt-3 p-3 dbn-nft-gallery">
      {/* TODO:fix centering */}
      {loading && <LoadingText />}
      
      {!loading && 
        makeList(presentTokens)
      }
    </div>

  )
}

export default Gallery;
