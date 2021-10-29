import React, {useState, useRef, useEffect} from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

import CodeMirror from '@uiw/react-codemirror';
import {keymap, highlightSpecialChars, drawSelection, highlightActiveLine} from "@codemirror/view"
import {Extension, EditorState} from "@codemirror/state"
import {history, historyKeymap} from "@codemirror/history"
import {foldGutter, foldKeymap} from "@codemirror/fold"
import {indentOnInput} from "@codemirror/language"
import {lineNumbers, highlightActiveLineGutter} from "@codemirror/gutter"
import {defaultKeymap} from "@codemirror/commands"
import {bracketMatching} from "@codemirror/matchbrackets"
import {closeBrackets, closeBracketsKeymap} from "@codemirror/closebrackets"
import {searchKeymap, highlightSelectionMatches} from "@codemirror/search"
import {autocompletion, completionKeymap} from "@codemirror/autocomplete"
import {commentKeymap} from "@codemirror/comment"
import {EditorView} from "@codemirror/view"
import {rectangularSelection} from "@codemirror/rectangular-selection"
import {defaultHighlightStyle} from "@codemirror/highlight"
import {lintKeymap} from "@codemirror/lint"
import { javascript } from '@codemirror/lang-javascript';

import {useHotkeys} from 'react-hotkeys-hook'


import {parser} from "./lezer/dbnparser.js"
import {foldNodeProp, foldInside, indentNodeProp, delimitedIndent} from "@codemirror/language"
import {styleTags, tags as t, HighlightStyle} from "@codemirror/highlight"
import {LRLanguage} from "@codemirror/language"
import {LanguageSupport} from "@codemirror/language"


let parserWithMetadata = parser.configure({
  props: [
    styleTags({
      BuiltinCommand: t.standard(t.function(t.variableName)),
      CommandIdentifier: t.function(t.variableName),

      ProcedureDef: t.keyword,
      Set: t.keyword,
      Repeat: t.keyword,
      Question: t.keyword,
      Value: t.keyword,
      Metadata: t.documentMeta,

      VariableSet: t.variableName,
      VariableGet: t.variableName,
      FormalArg: t.variableName,
      RepeatArg: t.variableName,
      NumberCall: t.function(t.variableName),

      Number: t.number,
      LineComment: t.lineComment,

      AddOperators: t.arithmeticOperator,
      MulOperators: t.arithmeticOperator,
      DotSet: t.derefOperator,
      DotGet: t.derefOperator,
    }),
    indentNodeProp.add({
       Block: delimitedIndent({closing: "}"})
    })
  ]
})

export const dbnLanguage = LRLanguage.define({
  parser: parserWithMetadata,
  languageData: {
    commentTokens: {line: "//"}
  },
})


const dbnftHighlightStyle = HighlightStyle.define([
  {tag: t.number, color: "#1717ab"},
  {tag: t.arithmeticOperator,  fontWeight: "bold" },
  {tag: t.derefOperator,  fontWeight: "bold" },
  {tag: t.keyword, fontWeight: "bold" },


  {tag: t.function(t.variableName), color: "#0f0f95", fontWeight: "bold"},
  {tag: t.standard(t.function(t.variableName)), color: "#0f0f95", fontWeight: "bold"},

  {tag: t.documentMeta, color: "red", fontWeight: "bold"},
  {tag: t.comment, color: "#4896bd", fontStyle: "italic"}
])

let disabledTheme = EditorView.theme({
  ".cm-content": {
    backgroundColor: "#f5f5f5"
  },
})

const baseExtensions = [
  lineNumbers(),
  highlightActiveLineGutter(),
  highlightSpecialChars(),
  history(),
  foldGutter(),
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
  const [usedKeyboardShortcutToRun, setUsedKeyboardShortcutToRun] = useState(false)

  const textarea = useRef(null)

  function onCodeChange(e) {
    setCode(e.target.value)
  }

  function onRunKeyboardShortcut() {
    setUsedKeyboardShortcutToRun(true)
    props.onRun(code);
    return true;
  }

  function onRunPress() {
    props.onRun(code)
  }

  useEffect(() => {
    if (!props.disabled) {
      if (usedKeyboardShortcutToRun) {
        editor.current.view.focus()
        setUsedKeyboardShortcutToRun(false)
      }
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
      keymap.of([
        {key: "Mod-Enter", run: onRunKeyboardShortcut},
        ...closeBracketsKeymap,
        ...defaultKeymap,
        ...historyKeymap,
        ...foldKeymap,
        ...commentKeymap,
        ...completionKeymap,
        ...lintKeymap,
      ]),
    ])
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
                    setCode(value)
                  }}
                  editable={!props.disabled}
                  autofocus={!props.disabled && usedKeyboardShortcutToRun}
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
