import random
import unittest

import parser
from dbnast import *
from tests.parser_tests.base_test import ParserTestCase


class ParseBlockStatementTest(ParserTestCase):
    """
    tests the parse_block_statement dispatcher
    """
    def test_parse_set(self):
        """
        it should parse a set
        """
        tokens = self.make_tokens(
            ('SET', ''),
            ('WORD', 'A'),
            ('NUMBER', '9'),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block_statement, tokens, expected=DBNSetNode)

    def test_parse_repeat(self):
        """
        it should parse a repeat
        """
        tokens = self.make_tokens(
            ('REPEAT', ''),
            ('WORD', 'A'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('OPENBRACE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block_statement, tokens, expected=DBNRepeatNode)
    
    def test_parse_question(self):
        """
        it should parse a question
        """
        tokens = self.make_tokens(
            ('QUESTION', 'Same'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('OPENBRACE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block_statement, tokens, expected=DBNQuestionNode)

    def test_command_invocation(self):
        """
        it should parse a comand invocation
        """
        tokens = self.make_tokens(
            ('WORD', 'Floo'),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block_statement, tokens, expected=DBNCommandNode)
    
    def test_absorb_newline(self):
        """
        it should absorb a newline with grace
        """
        tokens = self.make_tokens(
            ('NEWLINE', ''),
        )
        result = parser.parse_block_statement(tokens)
        
        self.assertIsNone(result)
        self.assertEquals(0, len(tokens))

    def test_bad_token(self):
        """
        it should throw a value error for an un-handleable token type
        """
        tokens = self.make_tokens(
            ('OPENBRACKET', '')
        )
        
        with self.assertRaises(ValueError):
            parser.parse_block_statement(tokens)


if __name__ == '__main__':
    unittest.main()