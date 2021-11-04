import React from 'react';

import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import { Icon } from '@iconify/react';


function FixedPill({label, value, maxWidth}) {
  return (
    <span class="badge rounded-pill bg-light text-dark ms-1">
      {label + ":"}
      <span
        className="dbn-image-control-bar-fixed-pill-content"
        style={{width: maxWidth + "ch"}}
      >
        {value}
      </span>
    </span>
  )
}

function ControlBar({
    canZoomIn,
    canZoomOut,
    onZoomIn,
    onZoomOut,
    magnfication,

    hoverX,
    hoverY,
    hoverColor,

    onToggleDarkmode,
    darkmode
  }) {
  return ( 
    <div className={"dbn-image-control-bar " + (darkmode ? "darkmode" : "")}>
      <Button className="me-2" variant="light" onClick={onToggleDarkmode}>
        {darkmode ?
          <Icon icon="oi:sun" inline={true} />
          :
          <Icon icon="oi:moon" inline={true} />
        }
      </Button>

      <ButtonGroup  aria-label="Basic example">
        <Button variant="light" disabled={!canZoomOut} onClick={onZoomOut}>
          <Icon icon="oi:zoom-out" inline={true} />
        </Button>

        <Button variant="light" disabled={!canZoomIn} onClick={onZoomIn}>
          <Icon icon="oi:zoom-in" inline={true}/>
        </Button>

        <Button variant="light" className="zoom-indicator" disabled={true}>
          {magnfication + "x"}
        </Button>
      </ButtonGroup>

        <div className="d-inline-block mx-2">
          <FixedPill label="X" value={hoverX} maxWidth={3} />
          <FixedPill label="Y" value={hoverY} maxWidth={3} />
          <FixedPill label="Pen" value={hoverColor} maxWidth={3} />
        </div>
    </div>
  )
}


export default ControlBar
