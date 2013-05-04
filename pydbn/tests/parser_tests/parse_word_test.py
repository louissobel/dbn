import unittest

import parser
from parser.structures.ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase

class ParseWordTest(ParserTestCase):
        
    def test_parse_word(self):
        """
        parser.parse_word should pop a token off
        and return a DBNWordNode
        """
        token_value = 'hi'
        tokens = self.make_tokens(('WORD', token_value))
        result, result_tokens = self.run_parse(parser.parse_word, tokens, expected=DBNWordNode)

        # and that it has its name set to the value of the token
        self.assertEqual(result.value, token_value)

    def test_failed_parse_word(self):
        """
        parser.parse_words should throw a ValueError
        if the top token on the stack is anything other than
        a NUMBER
        """
        token_value = 'hi'
        tokens = self.make_tokens(('NUMBER', token_value))

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_word, tokens)


if __name__ == "__main__":
    unittest.main()
