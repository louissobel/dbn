import flask

from tokenizer import DBNTokenizer
from parser import DBNParser

app = flask.Flask(__name__)
app.debug = True


tokenizer = DBNTokenizer()
parser = DBNParser()

@app.route('/compile', methods=('POST',))
def index():
    dbn_script = flask.request.stream.read()
    try:
        tokens = tokenizer.tokenize(dbn_script)
        dbn_ast = parser.parse(tokens)
        return dbn_ast.to_js(varname='ast')
    except Exception as e:
        return "var ast = null;"

if __name__ == "__main__":
    app.run('0.0.0.0', port=4000)