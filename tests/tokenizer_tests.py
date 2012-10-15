from __future__ import absolute_import

from tokenizer import DBNTokenizer

import unittest

def build_test_builder(function):
    def build_test(arg, expected):
        def test(self):
            self.assertEqual(function(arg), expected)
        return test
    return build_test




class TokenizerTest(unittest.TestCase):
    def test_bad_token(self):
        self.assertRaises(ValueError, tokenizer_tester, bad_input)


teststring1 = """horse ("""

teststring2 = """//comment
Set Repeat 98
house
goose //foo
Same?
*"""

teststring3 = """Set [0 9] A
Repeat {
    Line 0 0 (5 + 7 * [6 (G + 9)]) H //fancy thing
    Paper 6
    Woof
}"""
expected3 = [
    'SET',
    'OPENBRACKET',
    'NUMBER',
    'NUMBER',
    'CLOSEBRACKET',
    'WORD',
    'NEWLINE',
    'REPEAT',
    'OPENBRACE',
    'NEWLINE',
    'WORD',
    'NUMBER',
    'NUMBER',
    'OPENPAREN',
    'NUMBER',
    'OPERATOR',
    'NUMBER',
    'OPERATOR',
    'OPENBRACKET',
    'NUMBER',
    'OPENPAREN',
    'WORD',
    'OPERATOR',
    'NUMBER',
    'CLOSEPAREN',
    'CLOSEBRACKET',
    'CLOSEPAREN',
    'WORD',
    'NEWLINE',
    'WORD',
    'NUMBER',
    'NEWLINE',
    'WORD',
    'NEWLINE',
    'CLOSEBRACE',
]

test_string_load = """6
Load horse
Cow
"""

expected_load = [
    'NUMBER',
    'NEWLINE',
    'LOAD',
    'NEWLINE',
    'WORD',
    'NEWLINE',
]

bad_input = """
Pen 0
Paper 6
: Goo
"""

tokenizer_test_cases = [
    ("*", ['OPERATOR']),
    (teststring1, ['WORD', 'OPENPAREN']),
    (teststring2, ['NEWLINE', 'SET', 'REPEAT', 'NUMBER', 'NEWLINE', 'WORD', 'NEWLINE', 'WORD', 'NEWLINE', 'QUESTION', 'NEWLINE', 'OPERATOR']),
    (teststring3, expected3),
    (test_string_load, expected_load),
]

def tokenizer_tester(string):
    tokenizer = DBNTokenizer()
    return [token.type for token in tokenizer.tokenize(string)]

tokenizer_test_builder = build_test_builder(tokenizer_tester)
for index, (string, expected) in enumerate(tokenizer_test_cases):
    test_method = tokenizer_test_builder(string, expected)
    test_method.__name__ = "test_tokenizer_%d" % index
    setattr(TokenizerTest, test_method.__name__, test_method)
    
    
if __name__ == "__main__":
    unittest.main()

    