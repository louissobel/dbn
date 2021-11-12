import React, {useState} from 'react';

import classNames from 'classnames';

import Minter from '../minter/Minter'
import ImageViewer from '../shared/ImageViewer'
import ControlBar from './ControlBar'
import RenderStatus from './RenderStatus'


const MAX_MAGNIFICATION = 3

function ImageResult(props) {
  const [magnfication, setMagnification] = useState(props.initialMagnification || 2)
  const [hoveringOverPixel, setHoveringOverPixel] = useState(null)
  const [darkmode, setDarkmode] = useState(false)

  function toggleDarkmode() {
    setDarkmode(!darkmode)
  }

  function zoomUpdate(n) {
    setMagnification(magnfication + n)
  }

  return(
    <div className={classNames('dbn-image-result', {'darkmode': darkmode})}>
      <ControlBar
        canZoomIn={magnfication < MAX_MAGNIFICATION}
        onZoomIn={() => zoomUpdate(1)}
        canZoomOut={magnfication > 1}
        onZoomOut={() => zoomUpdate(-1)}
        magnfication={magnfication}

        hoverX={hoveringOverPixel?.x}
        hoverY={hoveringOverPixel?.y}
        hoverColor={hoveringOverPixel?.color}

        onToggleDarkmode={toggleDarkmode}
        darkmode={darkmode}

      />

      <div className="mx-auto dbn-image-viewer" style={{width: 101*MAX_MAGNIFICATION }}>
        <ImageViewer
          imageData={props.imageData}
          magnify={magnfication}
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
        gasUsed={props.gasUsed}
        darkmode={darkmode}
        onCancel={props.onCancel}
      />

    </div>
  )
}

export default ImageResult;
