/* eslint import/no-anonymous-default-export: "off" */

import {line, commentedLine, describedLine} from './line'
import {paper, paperCoveringLine} from './paper'
import {pen, simplePen} from './pen'

import variables from './variables'
import repeat from './repeat'
import math from './math'
import {questionSame, questionSmaller} from './questions'
import dots from './dots'

import squareCommand from './squareCommand'

export default {
  'line': line,
  'commentedLine': commentedLine,
  'describedLine': describedLine,
  'paper': paper,
  'paperCoveringLine': paperCoveringLine,
  'simplePen': simplePen,
  'pen': pen,
  'variables': variables,
  'repeat': repeat,
  'math': math,
  'questionSame': questionSame,
  'questionSmaller': questionSmaller,
  'dots': dots,
  'squareCommand': squareCommand,
}
