import React, {useState, useEffect, useRef} from 'react';

import { useHistory } from "react-router-dom";
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import { Icon } from '@iconify/react';

import UIEditableCodeMirror from './UIEditableCodeMirror'
import {SessionStorage, STORAGE_KEY_RESET_INITIAL_CODE} from '../storage'


// returns the different values for variables
function specDiff(currentSpec, newSpec) {
  if (currentSpec.length !== newSpec.length) {
    console.warn('can only handle value changes')
    return []
  }

  let out = []
  for (var i = 0; i < currentSpec.length; i++) {
    let currentItem = currentSpec[i];
    let newItem = newSpec[i];

    if (currentItem.type !== 'constant' && newItem.value !== currentItem.value) {
      out.push({
        name: currentItem.name,
        newValue: newItem.value,
      })
    }
  }
  return out
}

function InteractiveCodeAndImage({ linkageRef, example, noheaders, linkedExample }) {
  const canvasRef = useRef()

  const [spec, setSpec] = useState(example.initialSpec)
  const [tooltipItemName, setTooltipItemName] = useState(null)

  const code = useRef(null)
  const [interacted, setInteracted] = useState(false)
  const history = useHistory()

  const uiEditableDispatchRef = useRef(null)

  if (linkageRef) {
    linkageRef.current = {
      receivePropagatedChange(newSpec) {
        let actions = specDiff(spec, newSpec);
        console.log(actions, example.name, !!uiEditableDispatchRef.current)

        if (uiEditableDispatchRef.current) {
          for (let a of actions) {
            console.log(a)
            uiEditableDispatchRef.current(a)
          }
        }
      }
    }
  }

  useEffect(() => {
    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d')
    ctx.imageSmoothingEnabled = false

    example.draw(ctx, spec, tooltipItemName);
  }, [example, spec, tooltipItemName])

  
  function onChange(spec) {
    setSpec(spec)
    if (linkedExample && linkedExample.current) {
      linkedExample.current.receivePropagatedChange(spec)
    }
  }

  function onCodeChange(newCode) {
    const current = code.current;
    if (current !== null && current !== newCode) {
      setInteracted(true)
    }
    code.current = newCode;
  }

  function onGoEditClick(e) {
    e.preventDefault()
    let codeWithDescription = "//description: " + example.name + " example\n\n" + code.current;
    let encodedCode = encodeURIComponent(codeWithDescription)
    let url = '/create?initialCode=' + encodedCode;

    // There's an interesting behavior, where we seem
    // to copy over sessionStorage to this new window.
    // That's _not_ what we want, at least for the code
    // in the editor, because it interferes with replacing
    // it with whatever is coming from the reference examples.
    //
    // So set _another_ local storage field indicating
    // that we're coming from the reference and that
    // we should prioritize what is in the URL.
    if (SessionStorage.enabled) {
      SessionStorage.get().setItem(
        STORAGE_KEY_RESET_INITIAL_CODE,
        'true',
      )
    }
    window.open(url, "_blank");
    if (SessionStorage.enabled) {
      SessionStorage.get().removeItem(STORAGE_KEY_RESET_INITIAL_CODE)
    }
  }

  return (

    <Row className="dbn-reference-code-and-image">
      <Col xs={7}>
        <div>
          {interacted &&
            <div className="align-left dbn-reference-code-and-image-go-edit">
              <a href="#" onClick={onGoEditClick}>
                <Icon icon="oi:share-boxed" inline={true} />
              </a>
            </div>
          }
          {!noheaders && <h6>Input:</h6>}
        </div>
        <UIEditableCodeMirror
          initialSpec={example.initialSpec}
          dispatchRef={uiEditableDispatchRef}
          onChange={onChange}
          onCodeChange={onCodeChange}
          onVisibleTooltipChange={setTooltipItemName}
        />

      </Col>

      <Col xs={5}>
        {!noheaders && <h6>Output:</h6>}
        <canvas
          ref={canvasRef}
          height={121}
          width={121}
          style={{
            position: 'relative',
            top:'-10px',
            left: '-10px',
          }}
        />
      </Col>
    </Row>
  )
}

export default InteractiveCodeAndImage
