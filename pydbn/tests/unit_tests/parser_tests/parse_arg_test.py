import unittest

import parser
from parser.structures.ast_nodes import *
from tests.unit_tests.parser_tests.base_test import ParserTestCase


class ParseArgTest(ParserTestCase):
    """
    test the parse arg parser dispatcher
    """

    def test_parse_number(self):
        """
        parse args should parse a number
        """
        tokens = self.make_tokens(('NUMBER', '0'))
        result, result_tokens = self.run_parse(parser.parse_arg, tokens, expected=DBNNumberNode)
    
    def test_parse_word(self):
        """
        parse args should parse a word
        """
        tokens = self.make_tokens(('WORD', 'A'))
        result, result_tokens = self.run_parse(parser.parse_arg, tokens, expected=DBNWordNode)
    
    def test_parse_arithmetic(self):
        """
        parse args should parse an arithmetic
        """
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '3'),
            ('OPERATOR', '+'),
            ('NUMBER', '2'),
            ('CLOSEPAREN', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_arg, tokens, expected=DBNBinaryOpNode)
    
    def test_parse_bracket(self):
        """
        parse args should parse a bracket
        """
        tokens = self.make_tokens(
            ('OPENBRACKET', ''),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('CLOSEBRACKET', '')
        )
        result, result_tokens = self.run_parse(parser.parse_arg, tokens, expected=DBNBracketNode)

    def test_parse_number_call(self):
        """
        parse args should parse a number call
        """
        tokens = self.make_tokens(
            ('OPENANGLEBRACKET', ''),
            ('WORD', 'Line'),
            ('CLOSEANGLEBRACKET', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_arg, tokens, expected=DBNProcedureCallNode)

    def test_parse_error(self):
        """
        it should raise error if it is not one of the parseable tokens
        """
        tokens = self.make_tokens(('SET', ''))
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_arg, tokens, expected=DBNSetNode)


if __name__ == "__main__":
    unittest.main()
