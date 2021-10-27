import os
import sys
import json
import base64

import flask
from flask import abort

sys.path.insert(0, os.environ['DBNROOT'])
import pydbn
import pydbn.evm_compile_lambda

app = flask.Flask(__name__)
app.debug = True

dbn_compiler = pydbn.compiler.DBNCompiler()

@app.route('/compile', methods=('POST',))
def index():
    dbn_script = flask.request.stream.read().decode("utf-8")
    print(dbn_script)
    try:
        tokens = pydbn.parser.tokenize(dbn_script)
        print(tokens)
        dbn_ast = pydbn.parser.parse(tokens)
        print(dbn_ast)
        compilation = dbn_compiler.compile(dbn_ast)
        print(compilation)
        bytecodes = pydbn.compiler.assemble(compilation)
        print(bytecodes)
        return json.dumps([{'op': c.op, 'arg': c.arg} for c in bytecodes])
    except Exception as e:
        return str(e)


@app.route('/evm_compile', methods=('POST',))
def evm_compile():
    input_data = base64.b64encode(flask.request.stream.read())

    response = pydbn.evm_compile_lambda.handler({
        'body': input_data,
        'isBase64Encoded': True,
    }, None)

    if response['statusCode'] != 200:
        abort(response['statusCode'], response['body'])

    return response['body']

if __name__ == "__main__":
    app.run('0.0.0.0', port=4000)