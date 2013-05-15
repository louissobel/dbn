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
            ('OPENANGLEBRACKET', ''),
            ('WORD', 'Line'),
            ('CLOSEANGLEBRACKET', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_number_call, tokens, expected=DBNProcedureCallNode)

        self.assertIsInstance(result.children[0], DBNWordNode)
        self.assertEqual('Line', result.children[0].value)
        self.assertEqual(1, len(result.children))
        self.assertEqual('number', result.value)

    def test_args(self):
        """
        with arguments
        """
        tokens = self.make_tokens(
            ('OPENANGLEBRACKET', ''),
            ('WORD', 'Floop'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('CLOSEANGLEBRACKET', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_number_call, tokens, expected=DBNProcedureCallNode)

        self.assertEqual(3, len(result.children))
        for type_, child in zip((DBNWordNode, DBNNumberNode, DBNNumberNode), result.children):
            self.assertIsInstance(child, type_)

        self.assertEqual('Floop', result.children[0].value)
        self.assertEqual('number', result.value)


if __name__ == "__main__":
    unittest.main()
