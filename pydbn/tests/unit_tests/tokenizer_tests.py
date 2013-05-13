from parser import DBNTokenizer

import unittest


class TokenizerTestCase(unittest.TestCase):

    def tokenize(self, input_string, expected=None):
        tokenizer = DBNTokenizer()
        out = [token.type for token in tokenizer.tokenize(input_string)]

        if expected is not None:
            self.assertEqual(out, expected)

    def run_tokenizer_test(self):
        self.tokenize(self.input_string, self.expected)


class TestBadToken(TokenizerTestCase):

    def runTest(self):
        bad_input = """
Pen 0
Paper 6
: Goo
"""
        with self.assertRaises(ValueError):
            self.tokenize(bad_input)


class TestAnotherBadToken(TokenizerTestCase):
    """
    Regression:
    http://stackoverflow.com/questions/15992879/possible-bug-in-python-re
    """

    def runTest(self):
        bad_input = "."
        with self.assertRaises(ValueError):
            self.tokenize(bad_input)


class Test1(TokenizerTestCase):
    input_string = "*"
    expected = ['OPERATOR', 'NEWLINE']
    runTest = TokenizerTestCase.run_tokenizer_test

class Test2(TokenizerTestCase):
    input_string = """horse ("""
    expected = ['WORD', 'OPENPAREN', 'NEWLINE']
    runTest = TokenizerTestCase.run_tokenizer_test

class Test3(TokenizerTestCase):
    input_string = """//comment
Set Repeat 98
house
goose //foo
Same? Value
*"""
    expected = [
        'NEWLINE',
        'SET',
        'REPEAT',
        'NUMBER',
        'NEWLINE',
        'WORD',
        'NEWLINE',
        'WORD',
        'NEWLINE',
        'QUESTION',
        'VALUE',
        'NEWLINE',
        'OPERATOR',
        'NEWLINE',
    ]
    runTest = TokenizerTestCase.run_tokenizer_test


class Test4(TokenizerTestCase):
    input_string = """Set [0 9] A
Repeat {
    Line 0 0 (5 + 7 * [6 (G + 9)]) H //fancy thing
    Paper 6
    Woof <
    Command foob >
}"""
    expected = [
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
        'OPENANGLEBRACKET',
        'NEWLINE',
        'COMMAND',
        'WORD',
        'CLOSEANGLEBRACKET',
        'NEWLINE',
        'CLOSEBRACE',
        'NEWLINE',
    ]
    runTest = TokenizerTestCase.run_tokenizer_test


class Test5(TokenizerTestCase):
    """
    For the PATH token
    """
    input_string = "Load /foo/ba_r.dbn"
    expected = ['LOAD', 'PATH', 'NEWLINE']
    runTest = TokenizerTestCase.run_tokenizer_test


class Test6(TokenizerTestCase):
    """
    For value stuff
    """
    input_string = """Value <> Command Number"""
    expected=['VALUE', 'OPENANGLEBRACKET', 'CLOSEANGLEBRACKET', 'COMMAND', 'NUMBERDEF', 'NEWLINE']
    runTest = TokenizerTestCase.run_tokenizer_test


if __name__ == "__main__":
    unittest.main()

