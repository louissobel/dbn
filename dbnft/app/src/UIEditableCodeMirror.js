
import React, {useState, useRef, useEffect, useReducer} from 'react';
import ReactDOM from 'react-dom'
import classNames from 'classnames';

import Slider from 'rc-slider'
import 'rc-slider/assets/index.css'

import CodeMirror from '@uiw/react-codemirror';
import {dbnLanguage, dbnftHighlightStyle} from './lang-dbn/dbn'

import {StateField, EditorSelection} from "@codemirror/state"
import {drawSelection} from "@codemirror/view"
import {lineNumbers} from "@codemirror/gutter"
import {EditorView} from "@codemirror/view"


// not "width" or "height" because alignmet can change
const SLIDER_LENGTH = 101 + 10*2;
const SLIDER_BREADTH = 20;

function SpecItemSlider(props) {
  const vertical = props.alignment === 'vertical';

  const value = props.spec.find((s) => {
      return s.name === props.controls
  }).value

  function onChange(newValue) {
    props.dispatch({
      name: props.controls,
      newValue: newValue,
      type: 'new_value',
    })
  }

  var handleStyle = {}
  if (props.colorPicker) {
    let color = 255 * (1 - value / 100.0)
    handleStyle['backgroundColor'] = `rgb(${color}, ${color}, ${color})`

    // handle contrast against the grey overall tooltip background
    // TODO: is that the final tooltip background?
    if (value < 35) {
      handleStyle['border'] = '1px solid rgb(170, 170, 170)'
    }
  }

  return (
    <div
      className={classNames(
        "dbn-ui-editable-tooltip-holder",
        {'dbn-ui-editable-tooltip-holder-vertical': vertical},
        {'dbn-ui-editable-tooltip-holder-colorpicker': props.colorPicker}
      )}

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
        value={value}
        onChange={onChange}
        handleStyle={handleStyle}
      />
    </div>
  )
}

function composeString(spec) {

  var startOfLine = true;
  var out = "";

  for (let item of spec) {
    if (item.type === 'constant' && item.value === "\n") {
      out += "\n"
      startOfLine = true
    } else {
      if (startOfLine) {
        out += item.value
        startOfLine = false
      } else {
        out += " " + item.value;
      }
    }
  }

  return out;
}

function findSpecItemAndStartPosAt(spec, pos) {
  var i = 0;
  var startOfLine = true

  for (let item of spec) {
    if (item.type === 'constant' && item.value === "\n") {
      if (pos === i) {
        return {
          startPos: i,
          item: item,
        }
      }
      i += 1
      startOfLine = true
      continue
    } else {
      if (startOfLine) {
        startOfLine = false
      } else {
        i += 1 // for the space
      }
    }

    let end = i + item.value.length;
    if (pos >= i && pos <= end) {
      return {
        startPos: i,
        item: item,
      }
    }
    i += item.value.length

  }
  throw new Error("this shouldn't happen....")
}

function specReducer(currentSpec, action) {
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
  return newSpec;
}

function UIEditableCodeMirror(props) {
  const [spec, dispatch] = useReducer(specReducer, props.initialSpec)

  useEffect(() => {
    if (props.onChange) {
      props.onChange(spec);
    }
  }, [spec])
  
  const [activeSpecItem, setActiveSpecItem] = useState(null)
  const [tooltipCoords, setTooltipCoords] = useState(null)
  const [containerHasFocus, setContainerHasFocus] = useState(false)

  const tooltipShowing = containerHasFocus && activeSpecItem && tooltipCoords
  const code = composeString(spec)

  const editorRef = useRef()
  const containerRef = useRef()

  function ensureActiveSpecItem(nextItem) {
    if (!nextItem) {
      if (activeSpecItem !== null) {
        setActiveSpecItem(null)
      }
    } else {
      if (!activeSpecItem || activeSpecItem.name !== nextItem.name) {
        setTooltipCoords(null)
        setActiveSpecItem(nextItem)
        console.log(nextItem)
      }
    }
  }

  // onVisibleTooltipChange callback
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

  // clearing selection on focus out
  useEffect(() => {
    if (!containerHasFocus) {
      const view = editorRef.current.view;
      if (!view) {
        return
      }

      view.dispatch({
        selection: EditorSelection.single(0)
      })
    }
  }, [containerHasFocus])

  function handleEditorUpdate(viewUpdate) {
    const view = viewUpdate.view;

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
    let {startPos, item} = findSpecItemAndStartPosAt(spec, range.from)

    var expectedSelection
    if (item.type === 'constant') {
      expectedSelection = EditorSelection.single(startPos)

      ensureActiveSpecItem(null)
    } else {
      let expectedTo = startPos
      let expectedFrom = startPos + item.value.length
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

    if (!activeSpecItem) {
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

        // move this state update _out_ of the core measure writeback
        // this avoids situations where we trigger a re-render while
        // an editor update is actually in progress
        setTimeout(() => {
          setTooltipCoords({left, top})
        }, 0)
      }
    })
  }, [activeSpecItem])

  return (
    <div>
      <div
        ref={containerRef}
        className="dbn-ui-editable-code-wrapper"
        onFocus={() => setContainerHasFocus(true)}
        onBlur={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget)) {
            setContainerHasFocus(false)
          }
        }}
      >
        <CodeMirror
          //value={code}
          ref={editorRef}
          //height="350px"
          extensions={[
            lineNumbers(),
            drawSelection(),
            dbnLanguage,
            dbnftHighlightStyle,
          ]}
          autoFocus={false}
          onUpdate={handleEditorUpdate}
          editable={true}
          basicSetup={false}
        />

        {tooltipShowing &&

          <SpecItemSlider
            alignment={activeSpecItem.type === 'ycoord' ? 'vertical' : 'horizontal'}
            colorPicker={activeSpecItem.type === 'color'}
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
