import React, {useState, useEffect, useRef, useCallback} from 'react';
import { ErrorBoundary } from '@rollbar/react'

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

function InteractiveCodeAndImage({ linkageRef, example, noheaders, linkedExample, titleImage, clock }) {
  const canvasRef = useRef()

  const [spec, setSpec] = useState(example.initialSpec)
  const [tooltipItemName, setTooltipItemName] = useState(null)

  const code = useRef(null)
  const [, setInteracted] = useState(false)

  const uiEditableDispatchRef = useRef(null)

  if (linkageRef) {
    linkageRef.current = {
      receivePropagatedChange(newSpec) {
        let actions = specDiff(spec, newSpec);

        if (uiEditableDispatchRef.current) {
          for (let a of actions) {
            uiEditableDispatchRef.current(a)
          }
        }
      }
    }
  }

  const render = useCallback(() => {
    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d')
    ctx.imageSmoothingEnabled = false

    example.draw(ctx, spec, tooltipItemName);
  }, [example, spec, tooltipItemName])

  useEffect(() => {
    if (clock) {
      let interval = setInterval(render, 1000)

      return () => {
        clearInterval(interval)
      }
    }
  }, [clock, render])

  useEffect(render, [render])

  
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
          {
            <div className="align-left dbn-reference-code-and-image-go-edit">
              <a href="/create" onClick={onGoEditClick}>
                <Icon icon="oi:share-boxed" inline={true} />
              </a>
            </div>
          }
          {!noheaders && <h6>Input:</h6>}
        </div>
        <ErrorBoundary
          logMessage="UIEditableCodeMirror crash"
          fallbackUI={() => (
            <div className="dbn-ui-editable-code-wrapper crashed">
              Interactive example crashed! This is unexpected,
              but reloading the page should fix it.
            </div>
          )}
        >
          <UIEditableCodeMirror
            initialSpec={example.initialSpec}
            dispatchRef={uiEditableDispatchRef}
            onChange={onChange}
            onCodeChange={onCodeChange}
            onVisibleTooltipChange={setTooltipItemName}
          />
        </ErrorBoundary>

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

        {titleImage &&
          <div
            style={{
              position: 'relative',
              top:'-20px',
              fontWeight: 'bold',
            }}
          >{titleImage}</div>
        }
      </Col>
    </Row>
  )
}

export default InteractiveCodeAndImage
