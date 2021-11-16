import React, {useState, useRef, useEffect} from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';

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

import {dbnLanguage, dbnftHighlightStyle, maybeExtractDescription} from '../lang-dbn/dbn'

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


function LinkCopiedNotification({copiedAt}) {
  const [show, setShow] = useState(false)
  const currentTimer = useRef(null)

  useEffect(() => {
    if (copiedAt) {
      if (currentTimer.current) {
        clearTimeout(currentTimer.current)
        currentTimer.current = null
      }

      setShow(true)
      currentTimer.current = setTimeout(() => {
        setShow(false)
      }, 1200)

      return () => {
        clearTimeout(currentTimer.current)
      }
    }
  }, [copiedAt])

  
  return (
    <div className={"code-input-share-status " + (show ? '' : 'hidden')}>
      Link copied
    </div>
  )    
  

}

export default function CodeInput(props) {
  const editor = useRef();
  const filePicker = useRef();
  const [code, setCode] = useState(props.initialCode)
  const [description, setDescription] = useState(null)

  const previousBlobURL = useRef(null);
  const [codeBlobURL, setCodeBlobURL] = useState(null)
  const [shareLinkLastCopiedAt, setShareLinkLastCopiedAt] = useState(null)

  const [editedAfterRun, setEditedAfterRun] = useState(false)
  const lastRunViaKeyboard = useRef(false)

  const onChangeCallback = props.onChange;
  useEffect(() => {
    setEditedAfterRun(true)

    if (onChangeCallback) {
      onChangeCallback(code)
    }

    setCodeBlobURL(getBlobURLForCode(code))
    setDescription(maybeExtractDescription(code));
  }, [code, onChangeCallback])

  function onRunKeyboardShortcut() {
    // ignore if we're disabled
    if (props.disabled) {
      return;
    }

    lastRunViaKeyboard.current = true;
    props.onRun(code);
    return true;
  }

  function onRunPress() {
    lastRunViaKeyboard.current = false;
    props.onRun(code)
  }

  function getBlobURLForCode(code) {
    let blob = new Blob([code])
    return URL.createObjectURL(blob)
  }

  // Make sure we free it..
  useEffect(() => {
    let previous = previousBlobURL.current
    if (previous) {
      URL.revokeObjectURL(previous)
    }
    previousBlobURL.current = codeBlobURL

  }, [codeBlobURL])

  function onOpenPress() {
    if (filePicker.current) {
      filePicker.current.click()
    }
  }

  function onSharePress(e) {
    setShareLinkLastCopiedAt(Date.now())
    e.preventDefault()
    let el = document.createElement('input')
    document.body.appendChild(el)
    el.type = 'text'
    el.value = e.target.href
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
  }

  function codeShareURL() {
    let encodedCode = encodeURIComponent(code)
    return '/create?initialCode=' + encodedCode;
  }

  function handleOpenFileChange(e) {
    let fileList = e.target.files;
    if (fileList.length !== 1) {
      console.warn('unexpected file list length handling file selection', fileList.length)
      return;
    }

    let file = fileList[0];
    file.text()
    .then((code) => {
      setCode(code);
      lastRunViaKeyboard.current = false;
      props.onRun(code)
    })

    e.target.value = "";
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

  function runKeyboardShortcutText() {
    if (navigator.platform.indexOf('Mac') !== -1) {
      return <span style={{fontSize: '0.7rem'}}>(⌘-⏎)</span>
    } else if (navigator.platform.indexOf('Win') !== -1) {
      return <span style={{fontSize: '0.7rem'}}>(ctrl-⏎)</span>
    } else {
      return null
    }
  }


  return (
    <div className="code-input-holder">
      <Row>
        <Col>
          <div className="code-input-codemirror-holder mt-3 mt-lg-0">
            <CodeMirror
                  ref={editor}
                  value={props.initialCode}
                  height="350px"
                  extensions={codemirrorExtensions()}
                  onChange={(value, viewUpdate) => {
                    setCode(value)
                  }}
                  editable={!props.disabled}
                  readOnly={props.disabled}
                  basicSetup={false}
            />
          </div>
        </Col>
      </Row>
      <Row className="pb-5">
        <Col sm={12} md={12} lg={6} xl={6}>
          <div className="d-grid gap-2 mt-3">
            <Button 
              variant="primary"
              size="lg"
              disabled={props.disabled}
              onClick={onRunPress}
            >
              Run {runKeyboardShortcutText()}
            </Button>
          </div>
        </Col>
        <Col className="d-lg-none d-xl-block" xl={1} />
        <Col sm={12} md={12} lg={6} xl={5}>
          <div className="d-grid gap-2 mt-3">
            <ButtonGroup>
              <Button
                size="sm"
                variant="secondary"
                href={codeBlobURL}
                download={(description || "drawing") + ".dbn"}
              >
                Download
              </Button>

              <Button
                size="sm"
                variant="secondary"
                onClick={onSharePress}
                href={codeShareURL()}
              >
                Share
              </Button>
              
              <Button
                size="sm"
                variant="secondary"
                onClick={onOpenPress}
                disabled={props.disabled}
              >
                Open
              </Button>
            </ButtonGroup>
            
            <LinkCopiedNotification copiedAt={shareLinkLastCopiedAt} />

            <input
              type="file"
              ref={filePicker}
              accept=".dbn,text/plain"
              onChange={handleOpenFileChange}
              className="d-none"
            />
          </div>
        </Col>
      </Row>
    </div>
  )
}
