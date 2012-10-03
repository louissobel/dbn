import sys

from tokenizer import DBNTokenizer
from parser import DBNParser
from state import DBNInterpreterState
import output


if __name__ == "__main__":
    filename = sys.argv[1]
    dbn_script = open(filename).read()

    tokenizer = DBNTokenizer()
    parser = DBNParser()

    tokens = tokenizer.tokenize(dbn_script)
    dbn_ast = parser.parse(tokens)

    state = DBNInterpreterState()
    state = dbn_ast.apply(state)
    
    output.draw_window(state.image._image)
    