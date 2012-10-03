from tokenizer import DBNTokenizer
from parser import DBNParser
from state import DBNInterpreterState

import output

test_string = """
Line 0 5 60 (a+[0 3])
Repeat A 0 50
// foobee doobee woobe
{
    Paper (a * 3 + 6 / 4) // some comment
    Pen 100
}
"""

plain_test_string = """
Line 0 5 60 (a+[0 3])
Paper 100
Paper 20
Pen 50
Line 0 5 70 (a + [0 (b + 6 * 8 / (8 + c))])
Set A 60
Set [5 5] 50
"""

good_test = """
Paper 0
Set [50 50] 100
Paper 50
"""

arithmetic_test_string = """
Set A (5 + 4 * 9)
"""

tokenizer = DBNTokenizer()
parser = DBNParser()

tokens = tokenizer.tokenize(good_test)

for token in tokens:
    print token
dbn_ast = parser.parse(tokens)

dbn_ast.pprint()

state = DBNInterpreterState()
state = dbn_ast.apply(state)
print state.env
output.draw_window(state.image._image)


