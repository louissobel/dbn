import random
import unittest

import parser
from parser.structures.ast_nodes import *
from tests.unit_tests.parser_tests.base_test import ParserTestCase


class ParseCommandCallTest(ParserTestCase):
    """
    tests the parse_command_call (command invocation)
    """
    def test_noargs(self):
        """
        with no args
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('WORD', 'Line'),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )
        result, result_tokens = self.run_parse(parser.parse_command_call, tokens, expected=DBNProcedureCallNode, line_no=line_no)

        self.assertIsInstance(result.children[0], DBNWordNode)
        self.assertEqual('Line', result.children[0].value)
        self.assertEqual(1, len(result.children))
        self.assertEqual('command', result.value)

    def test_args(self):
        """
        with arguments
        """
        tokens = self.make_tokens(
            ('WORD', 'Floop'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('NEWLINE', '\n'),
        )
        result, result_tokens = self.run_parse(parser.parse_command_call, tokens, expected=DBNProcedureCallNode)

        self.assertEqual(3, len(result.children))
        for type_, child in zip((DBNWordNode, DBNNumberNode, DBNNumberNode), result.children):
            self.assertIsInstance(child, type_)

        self.assertEqual('Floop', result.children[0].value)
        self.assertEqual('command', result.value)

    def test_missing_newline(self):
        """
        should throw a value error (rare)
        """
        tokens = self.make_tokens(
            ('WORD', 'Floop'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_command_call, tokens, expected=DBNProcedureCallNode)


if __name__ == "__main__":
    unittest.main()
