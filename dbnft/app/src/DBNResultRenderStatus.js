import React from 'react';

import NumberFormat from 'react-number-format';
import classNames from 'classnames';

import StatusDot from './StatusDot'

function GasStats({gasUsed}) {
  return (
    <div class="d-inline ms-2 dbn-image-render-status-stats">
      Gas: <NumberFormat
        value={gasUsed}
        displayType={'text'}
        thousandSeparator={true}
      />
    </div>
  )
}

function BytecodeStats({codeSize}) {
  return (
    <div class="d-inline ms-2 dbn-image-render-status-stats">
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
  } else {
    console.error('unhandled error type in render status', renderError)
    return 'Error (' + renderError.type + ')'
  }
}

function DBNResultRenderStatus({renderState, renderError, codeSize, gasUsed, darkmode}) {

  var status;
  switch (renderState) {
    case "INITIAL":
      status = (
        <>
          <div class="d-inline me-1">
            <StatusDot />
          </div>

          No drawing — hit "Run" to render
        </>
      );
      break;
    case "RENDERING":
      status = (
        <>
          <div class="d-inline me-1">
            <StatusDot pending />
          </div>

          <span class="dbn-image-render-status-message">
            Rendering...
          </span>

          {codeSize && <BytecodeStats codeSize={codeSize} />}
          {gasUsed && <GasStats gasUsed={gasUsed} />}
        </>
      );
      break;
    case "DONE":
      status = (
        <>
          <div class="d-inline me-1">
            <StatusDot ok />
          </div>
          
          <span class="dbn-image-render-status-message">
            OK!
          </span>

          <BytecodeStats codeSize={codeSize} />
          <GasStats gasUsed={gasUsed} />

        </>
      );
      break;
    case "ERROR":
      status = (
        <>
          <div class="d-inline me-1">
            <StatusDot error />
          </div>

          <span class="dbn-image-render-status-message">
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


export default DBNResultRenderStatus
