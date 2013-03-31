import random

import parser
from dbnast import *
from tests.parser_tests.base_test import ParserTestCase


class ParseCommandTest(ParserTestCase):
    """
    tests the parse_command (command invocation)
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
        result, result_tokens = self.run_parse(parser.parse_command, tokens, expected=DBNCommandNode, line_no=line_no)
    
        self.assertEqual([], result.children)
        self.assertEqual('Line', result.name)
    
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
        result, result_tokens = self.run_parse(parser.parse_command, tokens, expected=DBNCommandNode)
        
        self.assertEqual(2, len(result.children))
        for type_, child in zip((DBNNumberNode, DBNNumberNode), result.children):
            self.assertIsInstance(child, type_)
    
        self.assertEqual('Floop', result.name)

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
            self.run_parse(parser.parse_command, tokens, expected=DBNCommandNode)