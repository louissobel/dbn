import random
import unittest

import parser
from parser.structures.ast_nodes import *
from tests.unit_tests.parser_tests.base_test import ParserTestCase


class ParseValueTest(ParserTestCase):
    """
    tests a value statement
    """
    def assert_value_node(self, result, type_):
        """
        asserts a value nodes structure
        """
        self.assertEquals(1, len(result.children))
        self.assertIsInstance(result.children[0], type_)

    def test_value(self):
        """
        value should work
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('VALUE', ''),
            ('WORD', 'A'),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )

        result, result_tokens = self.run_parse(parser.parse_value, tokens, expected=DBNValueNode, line_no=line_no)
        self.assert_value_node(result, DBNWordNode)

    def test_value_no_arg(self):
        """
        value should throw error if no arg
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('VALUE', ''),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )

        with self.assertRaises(ValueError):
            result, result_tokens = self.run_parse(parser.parse_value, tokens, expected=DBNValueNode)

    def test_value_no_newline(self):
        """
        value should throw an error if not newline terminated
        """
        tokens = self.make_tokens(
            ('VALUE', ''),
            ('NUMBER', '9'),
            # now some other token
            ('SET', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_value, tokens, expected=DBNSetNode)


if __name__ == "__main__":
    unittest.main()
