import sys
from optparse import OptionParser

from tokenizer import DBNTokenizer
from parser import DBNParser
from compiler import DBNCompiler
from interpreter import DBNInterpreter
import builtins

import output

option_parser = OptionParser()
option_parser.add_option('-c', '--compile', action="store_true", dest="compile", help="compile code", default=False)
option_parser.add_option('-n', '--numbers', action="store_true", dest="numbers", help="show opcode numbers", default=False)

option_parser.add_option('-t', '--trace', action="store_true", dest="trace", help="trace interpretation", default=False)


if __name__ == "__main__":
    (options, args) = option_parser.parse_args()

    filename = args[0]
    dbn_script = open(filename).read()
    tokenizer = DBNTokenizer()
    parser = DBNParser()
    compiler = DBNCompiler()
    
    tokens = tokenizer.tokenize(dbn_script)
    dbn_ast = parser.parse(tokens)
    compilation = compiler.compile(dbn_ast)

    if options.compile:
        for i, (o, a) in enumerate(compilation.bytecodes):
            if options.numbers:
                print "%d %s %s" % (i, str(o), str(a))
            else:
                print "%s %s" % (str(o), str(a))
    else:
        interpreter = DBNInterpreter(compilation.bytecodes)
        builtins.load_builtins(interpreter)
        interpreter.run(trace=options.trace)
        
        # ok!
        output.draw_window(interpreter.image._image)