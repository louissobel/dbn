import React from 'react';

import NumberFormat from 'react-number-format';

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

function DBNEditorRenderStatus({renderState, codeSize, gasUsed}) {

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
            Error!
          </span>
        </>
      );
      break;
  }

  return ( 
    <div className="dbn-image-render-status bg-light">
      {status}
    </div>
  )
}


export default DBNEditorRenderStatus
