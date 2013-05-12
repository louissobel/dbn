import os
import sys
import json

import flask

sys.path.insert(0, os.environ['DBNROOT'])
import compiler
import parser

app = flask.Flask(__name__)
app.debug = True

dbn_compiler = compiler.DBNCompiler()

@app.route('/compile', methods=('POST',))
def index():
    dbn_script = flask.request.stream.read()
    print dbn_script
    try:
        tokens = parser.tokenize(dbn_script)
        print tokens
        dbn_ast = parser.parse(tokens)
        print dbn_ast
        compilation = dbn_compiler.compile(dbn_ast)
        print compilation
        bytecodes = compiler.assemble(compilation)
        print bytecodes
        return json.dumps([{'op': c.op, 'arg': c.arg} for c in bytecodes])
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run('0.0.0.0', port=4000)