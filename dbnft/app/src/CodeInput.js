import React, {useState, useRef, useEffect} from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

import CodeMirror from '@uiw/react-codemirror';
import {keymap, highlightSpecialChars, drawSelection} from "@codemirror/view"
import {EditorState} from "@codemirror/state"
import {history, historyKeymap} from "@codemirror/history"
import {RangeSet} from "@codemirror/rangeset"
import {indentOnInput} from "@codemirror/language"
import {lineNumbers, highlightActiveLineGutter} from "@codemirror/gutter"
import {defaultKeymap} from "@codemirror/commands"
import {bracketMatching} from "@codemirror/matchbrackets"
import {closeBrackets, closeBracketsKeymap} from "@codemirror/closebrackets"
import {highlightSelectionMatches} from "@codemirror/search"
import {autocompletion, completionKeymap} from "@codemirror/autocomplete"
import {commentKeymap} from "@codemirror/comment"
import {EditorView, Decoration, ViewPlugin} from "@codemirror/view"
import {rectangularSelection} from "@codemirror/rectangular-selection"
import {defaultHighlightStyle} from "@codemirror/highlight"
import {lintKeymap} from "@codemirror/lint"
import {gutter, GutterMarker} from "@codemirror/gutter"



import {dbnLanguage, dbnftHighlightStyle} from './lang-dbn/dbn'

let disabledTheme = EditorView.theme({
  ".cm-content": {
    backgroundColor: "#f5f5f5"
  },
})

const gutterErrorMarker = new class extends GutterMarker {
  toDOM() { return document.createTextNode("🔺") }
}()

const baseExtensions = [
  lineNumbers(),
  highlightActiveLineGutter(),
  highlightSpecialChars(),
  history(),
  EditorState.allowMultipleSelections.of(true),
  indentOnInput(),
  defaultHighlightStyle.fallback,
  closeBrackets(),
  autocompletion(),
  rectangularSelection(),

  // TODO: add multiple highlights?
  dbnftHighlightStyle,

  dbnLanguage,
]
const editableExtensions = baseExtensions.concat([
    drawSelection(),
    highlightSelectionMatches(),
    bracketMatching(),
])
const disabledExtensions = baseExtensions.concat([
  disabledTheme,
])

export default function CodeInput(props) {
  const initial = `Line 0 0 100 100`

  const editor = useRef();
  const [code, setCode] = useState(initial)
  const [editedAfterRun, setEditedAfterRun] = useState(false)
  const lastRunViaKeyboard = useRef(false)

  function onCodeChange(code) {
    setEditedAfterRun(true)
    setCode(code)
  }

  function onRunKeyboardShortcut() {
    lastRunViaKeyboard.current = true;
    props.onRun(code);
    return true;
  }

  function onRunPress() {
    lastRunViaKeyboard.current = false;
    props.onRun(code)
  }

  useEffect(() => {
    if (!props.disabled) {
      if (lastRunViaKeyboard.current) {
        if (editor.current) {
          editor.current.view.focus()
        }
      }
      setEditedAfterRun(false)
    }
  }, [props.disabled])


  function codemirrorExtensions() {
    var extensions;
    if (props.disabled) {
      extensions = disabledExtensions;
    } else {
      extensions = editableExtensions;
    }

    return extensions.concat([
      errorGutter(),
      errorUnderline(),
      keymap.of([
        {key: "Mod-Enter", run: onRunKeyboardShortcut},
        ...closeBracketsKeymap,
        ...defaultKeymap,
        ...historyKeymap,
        ...commentKeymap,
        ...completionKeymap,
        ...lintKeymap,
      ]),
    ])
  }

  function errorGutter() {
    return gutter({
      lineMarker(view, block) {
        const line = view.state.doc.lineAt(block.from)

        if (!editedAfterRun && props.errorLines.includes(line.number)) {
          return gutterErrorMarker
        } else {
          return null
        }
      },
      initialSpacer: () => gutterErrorMarker
    })
  }

  function errorUnderline() {
    const underlineMark = Decoration.mark({class: "code-error-underline"})


    return ViewPlugin.fromClass(class {
      setDecorations(view) {
        if (props.errorLines && !editedAfterRun) {

          // RangeSet needs sorted input :/
          let sortedLines = props.errorLines.slice();
          sortedLines.sort((a, b) => {
            return a - b
          })

          this.decorations = RangeSet.of(sortedLines.flatMap((lineNumber) => {
            let line = view.state.doc.line(lineNumber);
            if (line.from === line.to) {
              return [];
            } else {
              return [underlineMark.range(line.from, line.to)]
            }
          }))
        } else {
          this.decorations = RangeSet.empty
        }
      }

      constructor(view) {
        this.setDecorations(view)
      }

      update(viewUpdate) {
        if (viewUpdate.docChanged) {
          this.decorations = RangeSet.empty
        }
      }
    }, {
      decorations: (v) => {
        return v.decorations
      }
    })
  }

  return (
    <div className="code-input-holder">
      <Row>
        <Col>
          <div className="code-input-codemirror-holder mt-3 mt-lg-0">
            <CodeMirror
                  ref={editor}
                  value={code}
                  height="350px"
                  extensions={codemirrorExtensions()}
                  onChange={(value, viewUpdate) => {
                    onCodeChange(value)
                  }}
                  editable={!props.disabled}
                  readOnly={props.disabled}
                  basicSetup={false}
            />
          </div>
        </Col>
      </Row>
      <Row>
        <Col sm={12} md={12} lg={8} xl={6}>
          <div className="d-grid gap-2 mt-3">
            <Button 
              variant="primary"
              size="lg"
              disabled={props.disabled}
              onClick={onRunPress}
            >
              Run
            </Button>
          </div>
        </Col>
      </Row>
    </div>
  )
}
