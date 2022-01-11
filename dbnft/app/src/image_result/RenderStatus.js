import React from 'react';

import NumberFormat from 'react-number-format';
import classNames from 'classnames';
import Button from 'react-bootstrap/Button';
import {Icon} from '@iconify/react'

import StatusDot from '../shared/StatusDot'

function RenderGasStats({inProgress, gasUsed, estimated}) {
  return (
    <div className="d-inline dbn-image-render-status-stats">
      {!inProgress && <span className="ms-2">Render: </span>}
      <span className={classNames(
        "dbn-image-render-status-render-gas-stat",
        {changing: inProgress}
      )}>
        {estimated ? '~' : ''}<NumberFormat
          value={gasUsed}
          displayType={'text'}
          thousandSeparator={true}
        />gas
      </span>
    </div>
  )
}

// This is rough linear regression; reflecting that
// cost will be dominated by linear-with-bytecode gas
function linearGasEstimate(codeSize) {
  return 1000 * Math.ceil(
    (183000 + codeSize*220) / 1000
  )
}

function MintGasEstimate({codeSize}) {
  let estimate = linearGasEstimate(codeSize)
  return (
    <div className="d-inline ms-2 dbn-image-render-status-stats">
      Mint: ~<NumberFormat
        value={estimate}
        displayType="text"
        thousandSeparator={true}
      />gas
    </div>
  )
}

function BytecodeStats({codeSize, onClick}) {
  return (
    <div
      className="d-inline ms-2 dbn-image-render-status-stats examinable"
      onClick={onClick}
    >
      Bytecode: {codeSize + "b"}
    </div>
  )
}

function errorMessage(renderError) {
  if (!renderError) {
    return 'Unhandled Error!'
  }

  if (!renderError.message) {
    console.error('error without message', renderError)
    return 'Error!'
  }

  if (renderError.type === 'parse') {
    return renderError.message + ' at line ' +  renderError.lineNumber;
  } else if (renderError.type === 'compile') {
    let message = renderError.message;
    if (renderError.lineNumber && !renderError.lineNumberInMessage) {
      message += " at line " + renderError.lineNumber
    }
    return message
  } else if (renderError.type === 'user_cancel') {
    return 'Cancelled'
  } else {
    console.error('unhandled error type in render status', renderError)
    return 'Error (' + renderError.type + ')'
  }
}

function RenderStatus({
    renderState,
    renderingOnChain,
    renderError,
    showMintGasEstimate,
    codeSize,
    gasUsed,
    onCancel,
    onRerun,
    darkmode,
    onBytecodeSizeClick
  }) {
  var status;
  switch (renderState) {
    case "INITIAL":
      status = (
        <>
          <div className="d-inline me-1">
            <StatusDot />
          </div>

          No drawing — hit "Run" to render
        </>
      );
      break;
    case "RENDERING":
      status = (
        <>
          <div className="d-inline me-1">
            <StatusDot pending />
          </div>

          <span className="dbn-image-render-status-message">
            Rendering... {renderingOnChain && '(on chain)'}
          </span>

          {gasUsed && <RenderGasStats inProgress estimated={renderingOnChain} gasUsed={gasUsed} />}
          {codeSize && <>
            <BytecodeStats codeSize={codeSize} onClick={onBytecodeSizeClick} />
            {showMintGasEstimate && <MintGasEstimate codeSize={codeSize} />}
          </>}

          {onCancel &&
            <div className={classNames(
              "float-end",
              "dbn-image-render-status-action",
              "dbn-image-render-status-cancel",
              {'darkmode': darkmode}
            )}>
              <Button size="sm" variant="light" onClick={onCancel}>
                <Icon icon="oi:x" inline={true} />
              </Button>
            </div>
          }
        </>
      );
      break;
    case "DONE":
      status = (
        <>
          <div className="d-inline me-1">
            <StatusDot ok />
          </div>
          
          <span className="dbn-image-render-status-message">
            OK! {renderingOnChain && '(on chain)'}
          </span>

          <RenderGasStats estimated={renderingOnChain} gasUsed={gasUsed} />
          <BytecodeStats codeSize={codeSize} onClick={onBytecodeSizeClick} />
          {showMintGasEstimate && <MintGasEstimate codeSize={codeSize} />}

          {onRerun &&
            <div className={classNames(
              "float-end",
              "dbn-image-render-status-action",
              "dbn-image-render-status-rerun",
              {'darkmode': darkmode}
            )}>
              <Button size="sm" variant="light" onClick={onRerun}>
                <Icon icon="oi:reload" inline={true} />
              </Button>
            </div>
          }

        </>
      );
      break;
    case "ERROR":
      status = (
        <>
          <div className="d-inline me-1">
            <StatusDot error />
          </div>

          <span className="dbn-image-render-status-message">
            {errorMessage(renderError)}
          </span>
        </>
      );
      break;
    default:
      throw new Error('unknown render state: ' + renderState);
  }

  return ( 
    <div className={classNames("dbn-image-render-status", "bg-light", {'darkmode': darkmode})}>
      {status}
    </div>
  )
}


export default RenderStatus
