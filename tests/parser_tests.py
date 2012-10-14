"""
Tests for general parser performance
"""

import unittest

from dbnast import *

from tokenizer import DBNToken

from parser import DBNParser

test1source = """
Paper 100
Pen 15
Repeat H 0 10 {
    Line [0 0] 100 0 100
    Set A 9
    Repeat B 0 H
    {
        Set [(B + H*7 / (6 + B)) 9] H
    }
}
"""
token_list = """
NEWLINE

WORD Paper
NUMBER 100
NEWLINE

WORD Pen
NUMBER 15
NEWLINE

REPEAT
WORD H
NUMBER 0
NUMBER 10
OPENBRACE
NEWLINE

WORD Line
OPENBRACKET
NUMBER 0
NUMBER 0
CLOSEBRACKET
NUMBER 100
NUMBER 0
NUMBER 100
NEWLINE

SET
WORD A
NUMBER 9
NEWLINE

REPEAT
WORD B
NUMBER 0
WORD H
NEWLINE

OPENBRACE
NEWLINE

SET
OPENBRACKET
OPENPAREN
WORD B
OPERATOR +
WORD H
OPERATOR *
NUMBER 7
OPERATOR /
OPENPAREN
NUMBER 6
OPERATOR +
WORD B
CLOSEPAREN
CLOSEPAREN
NUMBER 9
CLOSEBRACKET
WORD H
NEWLINE

CLOSEBRACE
NEWLINE

CLOSEBRACE
NEWLINE
"""

def build_tokens(string):
    out = []
    for line in string.split('\n'):
        if line:
            try:
                type_, value = line.split(' ')
            except ValueError: # Too many values to unpack
                type_, value = line, ''
            out.append(DBNToken(type_, value, 0, 0, line))
    return out

expected_ast = DBNBlockNode(
    DBNCommandNode('Paper', DBNNumberNode('100')),
    DBNCommandNode('Pen', DBNNumberNode('15')),
    DBNRepeatNode(DBNWordNode('H'), DBNNumberNode('0'), DBNNumberNode('10'), DBNBlockNode(
        DBNCommandNode('Line',
            DBNBracketNode(DBNNumberNode('0'), DBNNumberNode('0')),
            DBNNumberNode('100'),
            DBNNumberNode('0'),
            DBNNumberNode('100'),
        ),
        DBNSetNode(DBNWordNode('A'), DBNNumberNode('9')),
        DBNRepeatNode(DBNWordNode('B'), DBNNumberNode('0'), DBNWordNode('H'), DBNBlockNode(
            DBNSetNode(
                DBNBracketNode(
                    DBNBinaryOpNode('+',
                        DBNWordNode('B'),
                        DBNBinaryOpNode('/',
                            DBNBinaryOpNode('*',
                                DBNWordNode('H'),
                                DBNNumberNode('7')
                            ),
                            DBNBinaryOpNode('+',
                                DBNNumberNode('6'),
                                DBNWordNode('B'),
                            )
                        )
                    ),
                    DBNNumberNode('9')
                ),
                DBNWordNode('H'),
            ),
        )),
    )),
)

class ParserTestCase(unittest.TestCase):
    

    def test_parser_1(self):
        result = DBNParser().parse(build_tokens(token_list))
        self.assertEquals(str(result), str(expected_ast))
        


