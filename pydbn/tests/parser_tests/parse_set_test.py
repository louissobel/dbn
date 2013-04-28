import random
import unittest

import parser
from ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase


class ParseSetTest(ParserTestCase):
    """
    tests a set statement
    """
    def assert_set_node(self, result, types):
        """
        asserts a set nodes structure
        """
        self.assertEquals(2, len(result.children))
        
        for type_, child in zip(types, result.children):
            self.assertIsInstance(child, type_)
    
    def test_set_word(self):
        """
        set should set a word
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('SET', ''),
            ('WORD', 'A'),
            ('NUMBER', '9'),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )
        
        result, result_tokens = self.run_parse(parser.parse_set, tokens, expected=DBNSetNode, line_no=line_no)
        
        self.assert_set_node(result, (DBNWordNode, DBNNumberNode))
        
    def test_set_bracket(self):
        """
        set should set a bracket
        """
        tokens = self.make_tokens(
            ('SET', ''),
            ('OPENBRACKET', ''),
            ('NUMBER', '9'),
            ('NUMBER', '9'),
            ('CLOSEBRACKET', ''),
            ('NUMBER', '9'),
            ('NEWLINE', '\n'),
        )

        result, result_tokens = self.run_parse(parser.parse_set, tokens, expected=DBNSetNode)

        self.assert_set_node(result, (DBNBracketNode, DBNNumberNode))
    
    def test_set_bad_arg(self):
        """
        set should throw error if first arg is not settable
        """
        tokens = self.make_tokens(
            ('SET', ''),
            ('NUMBER', '0'),
            ('NUMBER', '9'),
            ('NEWLINE', '\n'),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_set, tokens, expected=DBNSetNode)
    
    def test_set_no_newline(self):
        """
        set should throw an error if not newline terminated
        """
        tokens = self.make_tokens(
            ('SET', ''),
            ('WORD', 'A'),
            ('NUMBER', '9'),
            # now some other token
            ('SET', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_set, tokens, expected=DBNSetNode)


if __name__ == "__main__":
    unittest.main()
