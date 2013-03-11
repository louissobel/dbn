import flask

import pydbn
import js_shim

app = flask.Flask(__name__)
app.debug = True

tokenizer = pydbn.tokenizer.DBNTokenizer()
parser = pydbn.parser.DBNParser()

@app.route('/compile', methods=('POST',))
def index():
    dbn_script = flask.request.stream.read()
    try:
        tokens = tokenizer.tokenize(dbn_script)
        dbn_ast = parser.parse(tokens)
        return js_shim.pydbn2dbnjs(dbn_ast)
    except Exception as e:
        return "null;"

if __name__ == "__main__":
    app.run('0.0.0.0', port=4000)