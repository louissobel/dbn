import {parser} from "./dbnparser.js"
import {indentNodeProp, delimitedIndent} from "@codemirror/language"
import {styleTags, tags as t, HighlightStyle} from "@codemirror/highlight"
import {LRLanguage} from "@codemirror/language"

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


// TODO: generalize this somehow?
export const dbnftHighlightStyle = HighlightStyle.define([
  {tag: t.number, color: "#1717ab"},
  {tag: t.arithmeticOperator,  fontWeight: "bold" },
  {tag: t.derefOperator,  fontWeight: "bold" },
  {tag: t.keyword, fontWeight: "bold" },


  {tag: t.function(t.variableName), color: "#0f0f95", fontWeight: "bold"},
  {tag: t.standard(t.function(t.variableName)), color: "#0f0f95", fontWeight: "bold"},

  {tag: t.documentMeta, color: "red", fontWeight: "bold"},
  {tag: t.comment, color: "#4896bd", fontStyle: "italic"}
])


export function maybeExtractDescription(code) {
  const firstLine = code.split("\n", 1)[0]
  const descriptionExtract = /^\/\/[Dd]escription: (.+)/
  const match = firstLine.match(descriptionExtract)
  if (match) {
    return match[1]
  } else {
    return null
  }
}

export function maybeExtractConfig(code) {
  const lines = code.split("\n", 2)
  let configLine = null;
  if (lines[0] && lines[0].startsWith("//config: ")) {
    configLine = lines[0]
  } else if (lines[1] && lines[1].startsWith("//config: ")) {
    configLine = lines[1]
  } else {
    return {}
  }

  // throw away the //config: at the start
  const parts = configLine.split(' ').slice(1)
  const config = {}
  for (let part of parts) {
    const kv = part.split('=')
    config[kv[0]] = JSON.parse(kv[1])
  }
  return config
}
