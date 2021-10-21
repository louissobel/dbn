import React, {useState, useRef, useEffect} from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

import {useHotkeys} from 'react-hotkeys-hook'

export default function CodeInput(props) {

  const [code, setCode] = useState("")
  const textarea = useRef(null)

  useHotkeys('command+enter', () => {
    props.onRun(code)
  }, {
    enableOnTags: ['TEXTAREA']
  });

  function onCodeChange(e) {
    setCode(e.target.value)
  }

  function onRunPress() {
    props.onRun(code)
  }

  return (
    <div className="code-input-holder">
      <Row>
        <Col>
          <textarea
            ref={textarea}
            className="code-input"
            cols="50"
            rows="12"
            disabled={props.disabled}
            value={code}
            onChange={onCodeChange}
          />
        </Col>
      </Row>
      <Row>
        <Col>
          <Button 
            variant="primary"
            disabled={props.disabled}
            onClick={onRunPress}
          >
            Run
          </Button>
        </Col>
      </Row>
    </div>
  )
}
