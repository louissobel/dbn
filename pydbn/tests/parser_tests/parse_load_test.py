import random
import unittest

import parser
from ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase


class ParseLoadTest(ParserTestCase):
    """
    tests a load statement
    """

    def test_load(self):
        """
        it should parse
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('LOAD', ''),
            ('PATH', 'foo.dbn'),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )

        result, result_tokens = self.run_parse(parser.parse_load, tokens, expected=DBNLoadNode, line_no=line_no)
        self.assertEquals('foo.dbn', result.name)

    def test_bad_arg(self):
        """
        load should throw an error if the arg is not a path
        """
        tokens = self.make_tokens(
            ('LOAD', ''),
            ('NUMBER', '0'),
            ('NEWLINE', '\n'),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_load, tokens, expected=DBNLoadNode)

    def test_load_no_newline(self):
        """
        load should throw an error if not newline terminated
        """
        tokens = self.make_tokens(
            ('LOAD', ''),
            ('PATH', 'foo.dbn'),
            # now some other token
            ('SET', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_load, tokens, expected=DBNLoadNode)


if __name__ == "__main__":
    unittest.main()
