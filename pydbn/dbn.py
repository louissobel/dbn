import sys
from optparse import OptionParser

from tokenizer import DBNTokenizer
from parser import DBNParser
from compiler import DBNCompiler
from interpreter import DBNInterpreter
import builtins

import output
import threading

option_parser = OptionParser()
option_parser.add_option('-c', '--compile', action="store_true", dest="compile", help="compile code", default=False)
option_parser.add_option('-n', '--numbers', action="store_true", dest="numbers", help="show opcode numbers", default=False)

option_parser.add_option('-f', '--file', action="store", dest="filename", help="file for output", default=None)
option_parser.add_option('-t', '--trace', action="store_true", dest="trace", help="trace interpretation", default=False)

def compile_dbn(filename):
    dbn_script = open(filename).read()
    tokenizer = DBNTokenizer()
    parser = DBNParser()
    compiler = DBNCompiler()

    tokens = tokenizer.tokenize(dbn_script)
    dbn_ast = parser.parse(tokens)
    compilation = compiler.compile(dbn_ast)
    return compilation

def run_dbn(compilation):
    interpreter = DBNInterpreter(compilation.bytecodes)
    builtins.load_builtins(interpreter)
    interpreter.run()
    return interpreter

if __name__ == "__main__":
    (options, args) = option_parser.parse_args()

    filename = args[0]
    compilation = compile_dbn(filename)

    if options.compile:
        for i, (o, a) in enumerate(compilation.bytecodes):
            if options.numbers:
                print "%d %s %s" % (i, str(o), str(a))
            else:
                print "%s %s" % (str(o), str(a))
    else:
        interpreter = DBNInterpreter(compilation.bytecodes)
        builtins.load_builtins(interpreter)

        if options.filename:
            # save it
            interpreter.run()
            output.output_png(interpreter, options.filename)

        else:
            threading.Thread(target = lambda: interpreter.run(trace=options.trace)).start()
            output.draw_window(interpreter)
        