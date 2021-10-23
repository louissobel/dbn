import os
import sys
import json

import flask
from flask import abort

sys.path.insert(0, os.environ['DBNROOT'])
import pydbn

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
    input_data = flask.request.json
    if input_data is None:
         abort(400, 'input data not json')

    print(input_data)
    dbn_script = input_data['code']
    input_metadata = input_data['metadata']
    metadata = pydbn.evm_compiler.Metadata(
        owning_contract=input_metadata.get('owning_contract'),
        description=input_metadata.get('description'),
    )

    print(dbn_script)
    print(metadata)

    tokens = pydbn.parser.tokenize(dbn_script)
    print(tokens)
    dbn_ast = pydbn.parser.parse(tokens)
    print(dbn_ast)
    compiler = pydbn.evm_compiler.DBNEVMCompiler(verbose=True)
    compilation = compiler.compile(
        dbn_ast,
        metadata=metadata,
    )
    return compilation



if __name__ == "__main__":
    app.run('0.0.0.0', port=4000)