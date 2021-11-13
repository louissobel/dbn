import React, {useState, useEffect} from 'react';

import classNames from 'classnames';

import {SessionStorage} from '../storage'
import Minter from '../minter/Minter'
import ImageViewer from '../shared/ImageViewer'
import ControlBar from './ControlBar'
import RenderStatus from './RenderStatus'


const MAX_MAGNIFICATION = 3

function ImageResult(props) {
  const [hoveringOverPixel, setHoveringOverPixel] = useState(null)

  let initialSettings = {
    darkmode: false,
    magnification: props.initialMagnification || 2,
  }
  const storageKey = 'dbnft.io-image-result-' + props.settingsStorageKey;
  if (props.settingsStorageKey) {
    if (SessionStorage.enabled) {
      const saved = SessionStorage.get().getItem(storageKey)
      if (saved) {
        console.log(saved)
        initialSettings = JSON.parse(saved)
      }
    }
  }

  const [darkmode, setDarkmode] = useState(initialSettings.darkmode)
  const [magnification, setMagnification] = useState(initialSettings.magnification)

  useEffect(() => {
    if (SessionStorage.enabled) {
      const settings = {
        darkmode: darkmode,
        magnification: magnification,
      }
      console.log(darkmode, magnification)
      SessionStorage.get().setItem(
        storageKey,
        JSON.stringify(settings),
      )

    }
  }, [darkmode, magnification])

  function toggleDarkmode() {
    setDarkmode(!darkmode)
  }

  function zoomUpdate(n) {
    setMagnification(magnification + n)
  }

  return(
    <div className={classNames('dbn-image-result', {'darkmode': darkmode})}>
      <ControlBar
        canZoomIn={magnification < MAX_MAGNIFICATION}
        onZoomIn={() => zoomUpdate(1)}
        canZoomOut={magnification > 1}
        onZoomOut={() => zoomUpdate(-1)}
        magnification={magnification}

        hoverX={hoveringOverPixel?.x}
        hoverY={hoveringOverPixel?.y}
        hoverColor={hoveringOverPixel?.color}

        onToggleDarkmode={toggleDarkmode}
        darkmode={darkmode}

      />

      <div className="mx-auto dbn-image-viewer" style={{width: 101*MAX_MAGNIFICATION }}>
        <ImageViewer
          imageData={props.imageData}
          magnify={magnification}
          onPixelHover={props.imageData && setHoveringOverPixel}
          extraClass="mx-auto"
        />
      </div>

      {props.description &&
        <div className={classNames('dbn-image-description', 'mt-1', {'darkmode': darkmode})}>
          <h5>{props.description}</h5>
        </div>
      }

      {props.showMinter &&
        <div className="mx-auto dbn-image-mint-controls">
          <Minter
            disabled={!props.minterEnabled}
            bytecode={props.bytecode}
            code={props.code}
            description={props.description}
            imageData={props.imageData}
            onMintInProgress={props.onMintInProgress}
            onMintabilityStatusChange={props.onMintabilityStatusChange}
          />
        </div>
      }

      <RenderStatus
        renderState={props.renderState}
        renderError={props.renderError}
        codeSize={props.bytecode ? (props.bytecode.length - 2)/2 : null}
        onBytecodeSizeClick={props.onShowCode}
        gasUsed={props.gasUsed}
        darkmode={darkmode}
        onCancel={props.onCancel}
      />

    </div>
  )
}

export default ImageResult;
