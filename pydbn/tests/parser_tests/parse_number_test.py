import unittest

import parser
from ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase

class ParseNumberTest(ParserTestCase):

    def test_parse_number(self):
        """
        parser.parse_number should successfully
        parse a NUMBER token, popping it off the stack
        """
        token_value = '9'
        tokens = self.make_tokens(('NUMBER', token_value))
        result, result_tokens = self.run_parse(parser.parse_number, tokens, expected=DBNNumberNode)

        # and that it has its name set to the value of the token
        self.assertEqual(result.name, token_value)
    
    def test_failed_parse_number(self):
        """
        parser.parse_number should throw a ValueError
        if the top token on the stack is anything other than
        a NUMBER
        """
        token_value = 'hi'
        tokens = self.make_tokens(('WORD', token_value))
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_number, tokens)


if __name__ == "__main__":
    unittest.main()
