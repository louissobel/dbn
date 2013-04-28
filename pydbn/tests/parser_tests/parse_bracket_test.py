import unittest

import parser
from ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase

class ParseBracketTest(ParserTestCase):
    
    def test_parse_bracket(self):
        """
        parser.parse_bracket should parse a bracket,
        removing it fully from the stack
        """
        # using numbers inside for simplicty,
        # the inner part is tested by parse_args
        tokens = self.make_tokens(
            ('OPENBRACKET', ''),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('CLOSEBRACKET', '')
        )
        result, result_tokens = self.run_parse(parser.parse_bracket, tokens, expected=DBNBracketNode)

        # check its children
        for child in result.children:
            self.assertIsInstance(child, DBNNumberNode)
        
        self.assertEquals(len(result.children), 2)
        self.assertEquals(result.children[0].name, '0')
        self.assertEquals(result.children[1].name, '100')


if __name__ == "__main__":
    unittest.main()
