import React, { useState, useEffect } from 'react';

import { useHistory } from "react-router-dom";
import { Icon } from '@iconify/react'
import { AutoSizer, List, WindowScroller } from 'react-virtualized'
import Alert from 'react-bootstrap/Alert';
import classNames from 'classnames'

import renderDBN from '../render'
import {dbnCoordinator} from '../eth_tools'
import LoadingText from '../shared/LoadingText'
import ImageViewer from '../shared/ImageViewer'

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

    // TODO: I think we need to grab the address too?
    // (I think that can be done in same call or something?)
    const bytecode = await dbnCoordinator.methods.tokenCode(this.tokenId).call()

    this._setRenderState('INTERPRETING')

    renderDBN(
      {bytecode: bytecode, workerPool: 'gallery'},
      (update, data) => {
        if (update === 'INTERPRET_PROGRESS') {
          if (data.imageData) {
            this._newImage(data.imageData)
          }
        }
      }
    )
    .then((renderResult) => {
      this.result = renderResult;
      this._newImage(renderResult.imageData)
      this._setRenderState('DONE')
    })
    .catch((e) => {
      this._setRenderState('ERROR')
      console.error('error rending', this.tokenId, e)
    })

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

  }, [present, id])


  function goToDetail() {
    history.push("/dbnft/" + id)
  }

  const showImageViewer = (renderState === 'INTERPRETING' || renderState === 'DONE' || renderState === 'ERROR')
  return (
    <div
      key={id}
      onClick={present ? goToDetail : null}
      className={classNames(
        "dbn-nft-gallery-item",
        {
          present: present,
          'image-viewer-present': showImageViewer,
        }
      )}
    >
       #{id}

        {showImageViewer &&
          <ImageViewer imageData={imageData} magnify={1}/>
        }

       {(renderState === 'LOADING_BYTECODE' || renderState === 'INTERPRETING') &&
         <div class="dbn-nft-gallery-item-status dbn-nft-gallery-item-loader">
           <Icon icon="mdi:ethereum" inline={true} />
         </div>
        }

       {(renderState === 'ERROR') &&
         <div class="dbn-nft-gallery-item-status dbn-nft-gallery-item-error">
           <Icon icon="oi:warning" inline={true} />
         </div>
        }
    </div>
  )
}

function Gallery() {
  const [loading, setLoading] = useState(true)
  const [rpcError, setRPCError] = useState(null)
  const [presentTokens, setPresentTokens] = useState(null)


  async function loadPresentTokens() {
    const allTokens = await dbnCoordinator.methods.allTokens().call()
    const presentTokens = {};
    for (let tokenId of allTokens) {
      presentTokens[tokenId] = true;
    }
    return presentTokens
  }


  useEffect(() => {
    loadPresentTokens()
    .then((presentTokens) => {
      setPresentTokens(presentTokens)
      setLoading(false)
    })
    .catch((e) => {
      setRPCError(e)
      console.error(e)
    })
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
                    tabIndex={null} // we don't want the whole list to be focusable
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
    <div className="pt-3 p-3 dbn-nft-gallery">
      {(loading && !rpcError) && <div className="text-center"><LoadingText /></div>}
      {(loading && rpcError) && 
        <Alert variant="danger">
          <p>Error getting token list</p>
          <p>{rpcError.toString()}</p>
        </Alert>
      }
      
      {!loading && 
        makeList(presentTokens)
      }
    </div>

  )
}

export default Gallery;
