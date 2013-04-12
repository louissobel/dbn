import unittest
import random

import parser
from dbnast import *
from tests.parser_tests.base_test import ParserTestCase

class ParseProgramTest(ParserTestCase):
    """
    tests parse block
    """
    def assert_block_node(self, result, child_types):
        """
        asserts block node
        """
        self.assertEquals(len(child_types), len(result.children))
        for type_, child in zip(child_types, result.children):
            self.assertIsInstance(child, type_)

    def test_parse_empty_program(self):
        """
        it should parse an empty program
        """
        tokens = []
        result, result_tokens = self.run_parse(parser.parse_program, tokens, expected=DBNProgramNode)
    
    def test_parse_just_newlines(self):
        """
        it should parse a program with just newlines
        """
        tokens = self.make_tokens(
            ('NEWLINE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_program, tokens, expected=DBNProgramNode)
        self.assert_block_node(result, (DBNNoopNode, DBNNoopNode))
    
    def test_parse_simple_program(self):
        """
        it will parse a nice little program
        """
        tokens = self.make_tokens(
            ('WORD', 'Pen'),
            ('NUMBER', '50'),
            ('NEWLINE', ''),
            
            ('WORD', 'Line'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('NUMBER', '100'),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_program, tokens, expected=DBNProgramNode)
        self.assert_block_node(result, (DBNCommandNode, DBNCommandNode))
        
    def test_no_trailing_newline_program(self):
        """
        it will throw value error if last statement is missing newline
        """
        tokens = self.make_tokens(
            ('WORD', 'Pen'),
            ('NUMBER', '50'),
            ('NEWLINE', ''),

            ('WORD', 'Line'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('NUMBER', '100'),
            # NO NEWLINE
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_program, tokens, expected=DBNProgramNode)
    
    def test_throw_error_bad_statement(self):
        """
        will throw a value error if given a bad statement
        """
        tokens = self.make_tokens(
            ('WORD', 'Pen'),
            ('NUMBER', '50'),
            ('NEWLINE', ''),

            ('NUMBER', '9'),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_program, tokens, expected=DBNProgramNode)
        
    def test_big_ol_program(self):
        """
        parses a big ol program
        """
        tokens = self.make_tokens(
             # noop
             ('NEWLINE', ''),
             
             # command_definition
             ('COMMAND', ''),
             ('WORD', 'Square'),
             ('OPENBRACE', ''),
             ('NEWLINE', ''),
             ('CLOSEBRACE', ''),
             ('NEWLINE', ''),

             # set
             ('SET', ''),
             ('WORD', 'A'),
             ('NUMBER', '9'),
             ('NEWLINE', ''),

             # noop
             ('NEWLINE', ''),

             # question
             ('QUESTION', 'Same?'),
             ('NUMBER', '0'),
             ('NUMBER', '0'),
             ('NEWLINE', '\n'),
             ('OPENBRACE', ''),
             ('NEWLINE', ''),
             ('CLOSEBRACE', ''),
             ('NEWLINE', '\n'),

             # command invocation
             ('WORD', 'Square'),
             ('NEWLINE', ''),

        )
        result, result_tokens = self.run_parse(parser.parse_program, tokens, expected=DBNProgramNode)
        self.assert_block_node(result,
            (DBNNoopNode, DBNCommandDefinitionNode, DBNSetNode, DBNNoopNode, DBNQuestionNode, DBNCommandNode)
        )
    

if __name__ == "__main__":
    unittest.main()
