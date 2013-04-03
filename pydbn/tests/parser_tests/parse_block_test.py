import unittest
import random

import parser
from dbnast import *
from tests.parser_tests.base_test import ParserTestCase

class ParseBlockTest(ParserTestCase):
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

    def test_parse_block(self):
        """
        parses a block!
        """
        tokens = self.make_tokens(
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block, tokens, expected=DBNBlockNode)
        self.assert_block_node(result, (DBNNoopNode, ))
        
    def test_parse_n_leading_newlines(self):
        """
        test that it randles arbitrary number of newlines, wihtout saving them
        """
        newline_count = random.randint(1, 10)
        newline_tokens = self.make_tokens(*[('NEWLINE', '') for i in range(newline_count)])
        tokens = newline_tokens + self.make_tokens(
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block, tokens, expected=DBNBlockNode)
        self.assert_block_node(result, (DBNNoopNode, ))

    def test_newline_after_brace_required(self):
        """
        test that an error is thrown unless there is a newline after the opening brace
        """
        tokens = self.make_tokens(
            ('OPENBRACE', ''),
            ('CLOSEBRACE', ''),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_block, tokens, expected=DBNBlockNode)
        
    def test_simple_block_parse(self):
        """
        tests a single statement block
        """
        tokens = self.make_tokens(
            ('OPENBRACE', ''),
            
            # noop
            ('NEWLINE', ''),
            
            # set
            ('SET', ''),
            ('WORD', 'A'),
            ('NUMBER', '9'),
            ('NEWLINE', ''),
            
            ('CLOSEBRACE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block, tokens, expected=DBNBlockNode)
        self.assert_block_node(result, (DBNNoopNode, DBNSetNode))

    def test_error_on_command(self):
        """
        will not parse a command_definition_statement
        """
        tokens = self.make_tokens(
            ('OPENBRACE', ''),
            
            # noop
            ('NEWLINE', ''),
            
            # command_definition
            ('COMMAND', ''),
            ('WORD', 'Square'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
            
            ('CLOSEBRACE', ''),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_block, tokens, expected=DBNBlockNode)
    
    def test_multi_statement_block(self):
        """
        tests a multi statement block
        """
        tokens = self.make_tokens(
            ('OPENBRACE', ''),
            
            # noop
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
            ('WORD', 'Foo'),
            ('NEWLINE', ''),
            
            ('CLOSEBRACE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_block, tokens, expected=DBNBlockNode)
        self.assert_block_node(result, (DBNNoopNode, DBNSetNode, DBNNoopNode, DBNQuestionNode, DBNCommandNode))
    # complicated statement
    
    

if __name__ == "__main__":
    unittest.main()
