import sys
from optparse import OptionParser

from tokenizer import DBNTokenizer
from parser import DBNParser
from dbnstate import DBNInterpreterState
import output

option_parser = OptionParser()
option_parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="verbose!", default=False)
option_parser.add_option('-a', '--animate', action="store_true", dest="animate", help="animate!", default=False)


(options, args) = option_parser.parse_args()


VERBOSE = options.verbose

filename = args[0]
dbn_script = open(filename).read()

tokenizer = DBNTokenizer()
parser = DBNParser()

tokens = tokenizer.tokenize(dbn_script)

if VERBOSE:
    for token in tokens:
        print token

dbn_ast = parser.parse(tokens)

if VERBOSE:
    dbn_ast.pprint()

state = DBNInterpreterState()

state = dbn_ast.apply(state)

if options.animate:
    # rewind the state
    first = state
    index = 0
    while first.previous is not None:
        print index
        index += 1
        first = first.previous
        
    output.animate_state(first, 'next')
else:
    output.draw_window(state.image._image)
