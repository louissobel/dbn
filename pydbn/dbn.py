import sys
from optparse import OptionParser

from tokenizer import DBNTokenizer
from parser import DBNParser
from dbnstate import DBNInterpreterState
import output

option_parser = OptionParser()
option_parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="verbose!", default=False)
option_parser.add_option('-a', '--animate', action="store_true", dest="animate", help="animate!", default=False)
option_parser.add_option('-j', '--javscript', action="store_true", dest="javascript", help="dump javascript", default=False)
option_parser.add_option('-l', '--line-numbers', action="store_true", dest="line_numbers", help="print line numbers!", default=False)
option_parser.add_option('-f', '--full', action="store_true", dest="full", help="full interface!", default=False)
option_parser.add_option('-t', '--time', action="store_true", dest="time", help="quit asap", default=False)


def run_script_text(dbn_script, **options):
    options = options or {}
    VERBOSE = options.get('verbose', False)
    dump_javascript = options.get('javascript', False)
    
    tokenizer = DBNTokenizer()
    parser = DBNParser()

    tokens = tokenizer.tokenize(dbn_script)

    if VERBOSE:
        for token in tokens:
            print token

    dbn_ast = parser.parse(tokens)
    if dump_javascript:
        print dbn_ast.to_js(varname='ast')

    if VERBOSE:
        dbn_ast.pprint()

    state = DBNInterpreterState()
    state = dbn_ast.apply(state)
    
    return state

if __name__ == "__main__":
    (options, args) = option_parser.parse_args()

    VERBOSE = options.verbose
    JAVASCRIPT = options.javascript

    try:
        filename = args[0]
        dbn_script = open(filename).read()
        
        state = run_script_text(dbn_script, verbose=VERBOSE, javascript=JAVASCRIPT)
        first = state
        while first.previous is not None:
            first = first.previous
    except IndexError:
        dbn_script = ''
        state = DBNInterpreterState()
        first = 5

    if options.animate: 
        output.animate_state(first, 'next')
    elif options.line_numbers:
        output.print_line_numbers(first)
    elif options.full:
        # we have to destroy local references to this huge ass state.
        # first save it in a container
        states = [state]
        del state
        del first
        output.full_interface(states, dbn_script)
    elif not JAVASCRIPT:
        output.draw_window(state.image._image, time=options.time)
