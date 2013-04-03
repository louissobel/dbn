import unittest

import parser
from dbnast import *
from tests.parser_tests.base_test import ParserTestCase

class ParseNewlineTest(ParserTestCase):
    
    def test_parse_newline(self):
        """
        should parse a newline, returning NOOPNODE
        """
        tokens = self.make_tokens(('NEWLINE', ''))
        result, result_tokens = self.run_parse(parser.parse_newline, tokens, expected=DBNNoopNode)
    
    def test_parse_newline_error(self):
        """
        should raise a value error for anything other than a newline
        """
        tokens = self.make_tokens(('SET', ''))
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_newline, tokens, expected=DBNNoopNode)

if __name__ == "__main__":
    unittest.main()
