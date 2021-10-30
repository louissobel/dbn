
import React, {useState, useRef, useEffect, useReducer} from 'react';
import ReactDOM from 'react-dom'
import classNames from 'classnames';

import Slider from 'rc-slider'
import 'rc-slider/assets/index.css'

import CodeMirror from '@uiw/react-codemirror';
import {dbnLanguage, dbnftHighlightStyle} from './lang-dbn/dbn'

import {Tooltip, showTooltip} from "@codemirror/tooltip"
import {StateField, EditorSelection} from "@codemirror/state"
import {drawSelection} from "@codemirror/view"
import {EditorView} from "@codemirror/view"


// not "width" or "height" because alignmet can change
const SLIDER_LENGTH = 101 + 10*2;
const SLIDER_BREADTH = 20;

function composeString(spec) {
  return spec.map((s) => {
    return s.value
  }).join(" ")
}

function findSpecItemAndStartPosAt(spec, pos) {
  var i = 0;

  for (let item of spec) {
    let end = i + item.value.length;
    if (pos >= i && pos <= end) {
      return {
        startPos: i,
        item: item,
      }
    }
    i += (item.value.length + 1) // +1 for space
  }
  throw new Error("this shouldn't happen....")
}

function SpecItemSlider(props) {
  const vertical = props.alignment === 'vertical';
  return (
    <div
      className={classNames(
        "dbn-ui-editable-tooltip-holder",
        {'dbn-ui-editable-tooltip-holder-vertical': vertical}
      )}
      onFocus={props.onFocus}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) {
          props.onBlur(e)
        }
      }}

      tabIndex={-1}
      style={{
        left: props.coords.left,
        top: props.coords.top,
      }}
    >
      <Slider
        vertical={vertical}
        min={0}
        max={100}
        value={
          props.spec.find((s) => {
              return s.name === props.controls
          }).value
        }
        onFocus={props.onFocus}
        onChange={(newValue) => 
          props.dispatch({
            name: props.controls,
            newValue: newValue,
            type: 'new_value',
          })
        }
      />
    </div>
  )
}

function UIEditableCodeMirror(props) {
  const [spec, dispatch] = useReducer((currentSpec, action) => {

    const newSpec = [];
    for (let item of currentSpec) {
      if (item.name === action.name) {
        newSpec.push({
          name: item.name,
          type: item.type,
          value: action.newValue.toString(),
        })
      } else {
        newSpec.push(item)
      }

    }

    if (props.onChange) {
      props.onChange(newSpec);
    }

    return newSpec;

  }, props.initialSpec)
  
  const [activeSpecItem, setActiveSpecItem] = useState(null)
  const [tooltipCoords, setTooltipCoords] = useState(null)
  const [editorHasFocus, setEditorHasFocus] = useState(false)
  const [tooltipHasFocus, setTooltipHasFocus] = useState(false)

  const showTooltip = editorHasFocus || tooltipHasFocus
  const tooltipShowing = showTooltip && activeSpecItem && tooltipCoords

  function ensureActiveSpecItem(nextItem) {
    if (!nextItem) {
      if (activeSpecItem !== null) {
        setActiveSpecItem(null)
      }
    } else {
      if (!activeSpecItem || activeSpecItem.name !== nextItem.name) {
        setActiveSpecItem(nextItem)
      }
    }
  }

  useEffect(() => {
    if (!props.onVisibleTooltipChange) {
      return
    }

    if (tooltipShowing) {
      props.onVisibleTooltipChange(activeSpecItem.name)
    } else {
      props.onVisibleTooltipChange(null)
    }
  }, [tooltipShowing, activeSpecItem])

  const code = composeString(spec)
  const editorRef = useRef()
  const containerRef = useRef()


  function handleEditorUpdate(viewUpdate) {
    const view = viewUpdate.view;

    if (viewUpdate.focusChanged) {
      setEditorHasFocus(view.hasFocus)
    }

    const currentValue = viewUpdate.state.doc.toString();
    const originalSelection = viewUpdate.startState.selection

    if (currentValue !== code) {
      let newSelection = originalSelection.main;
      if (newSelection.to > code.length) {
        newSelection.to = code.length
      }
      view.dispatch({
        changes: {
          from: 0,
          to: currentValue.length,
          insert: code,
        },
        selection: newSelection,
      });
    }

    // otherwise, might a selection change, figure out which
    // (if any) is the active item, and align selection to match
    const range = viewUpdate.state.selection.main;

    // Find whatever is under "from"
    let line = viewUpdate.state.doc.lineAt(range.head)
    let {startPos, item} = findSpecItemAndStartPosAt(spec, range.from - line.from)

    var expectedSelection
    if (item.type === 'constant') {
      expectedSelection = EditorSelection.single(startPos - line.from)

      ensureActiveSpecItem(null)
    } else {
      let expectedTo = startPos - line.from
      let expectedFrom = startPos + item.value.length - line.from
      expectedSelection = EditorSelection.single(expectedFrom, expectedTo)

      ensureActiveSpecItem(item)
    }

    if (!viewUpdate.state.selection.eq(expectedSelection)) {
      view.dispatch({
        selection: expectedSelection
      })
    }
    
  }

  useEffect(() => {
    const view = editorRef.current.view;
    const container = containerRef.current;
    if (!view || !container) {
      if (activeSpecItem !== null) {
        throw new Error('unable to position active spec item, no view or no container!')
      }
      return
    }

    view.requestMeasure({
      read: (view) => {
        return {
          cursorPos: view.coordsAtPos(view.state.selection.main.from),
          container: container.getBoundingClientRect(),
          lineHeight: view.defaultLineHeight,
        }
      },
      write: (measurements) => {
        const cursorLeft = measurements.cursorPos.left - measurements.container.left;
        const cursorTop = measurements.cursorPos.top - measurements.container.top;

        const vertical = activeSpecItem.type === 'ycoord'
        var left, top;
        if (vertical) {
          // Move over by 1 slider (and some room to breath)
          // left = cursorLeft - (SLIDER_BREADTH + 3);
          left = cursorLeft;

          // move it down
          top = cursorTop + measurements.lineHeight;
          // top = cursorTop - SLIDER_LENGTH/2 + measurements.lineHeight/2;
        } else {
          // Move down by 1 line
          top = cursorTop + measurements.lineHeight;
          // align to middle
          left = cursorLeft - SLIDER_LENGTH/2;
        }

        setTooltipCoords({left, top})
      }
    })
  }, [activeSpecItem])

  return (
    <div>
      <div ref={containerRef} className="dbn-ui-editable-code-wrapper">
        <CodeMirror
          //value={code}
          ref={editorRef}
          //height="350px"
          extensions={[
            drawSelection(),
            dbnLanguage,
            dbnftHighlightStyle,
            // cursorTooltipBaseTheme,
            // cursorTooltipField,
          ]}
          autoFocus={false}
          onUpdate={handleEditorUpdate}
          editable={true}
          basicSetup={false}
        />

        {tooltipShowing &&

          <SpecItemSlider
            alignment={activeSpecItem.type === 'ycoord' ? 'vertical' : 'horizontal'}
            onFocus={() => setTooltipHasFocus(true)}
            onBlur={() => setTooltipHasFocus(false)}
            coords={tooltipCoords}
            controls={activeSpecItem.name}
            spec={spec}
            dispatch={dispatch}
          />
        }
      </div>
      {/* this prevents clicks outside of the codemirror from getting sent to it */}
      &#8203;
    </div>
  )
}

export default UIEditableCodeMirror;
