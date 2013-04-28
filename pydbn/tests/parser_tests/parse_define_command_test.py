import unittest

import parser
from ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase

class ParseDefineCommandTest(ParserTestCase):
    """
    tests the parse_block function
    """
    def assert_define_command(self, result, name, argc):
        """
        asserts a define command node
        """
        self.assertEqual(result.children[0].name, name)
        self.assertEqual(len(result.children) - 2, argc)
        self.assertIsInstance(result.children[-1], DBNBlockNode)
    
    def test_define_command(self):
        """
        tests a noarg command defind
        """
        tokens = self.make_tokens(
            ('COMMAND', ''),
            ('WORD', 'Square'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_define_command, tokens, expected=DBNCommandDefinitionNode)
        self.assert_define_command(result, 'Square', 0)

    def test_define_command_with_args(self):
        """
        tests a noarg command defind
        """
        tokens = self.make_tokens(
            ('COMMAND', ''),
            ('WORD', 'Ploop'),
            ('WORD', 'X'),
            ('WORD', 'Y'),
            ('WORD', 'L'),
            ('WORD', 'R'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_define_command, tokens, expected=DBNCommandDefinitionNode)
        self.assert_define_command(result, 'Ploop', 4)
        
    def test_define_command_no_newline(self):
        """
        tests that an error is thrown without a terminating newline
        """
        tokens = self.make_tokens(
            ('COMMAND', ''),
            ('WORD', 'Square'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            
            # some other token besides newline
            ('SET', ''),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_define_command, tokens, expected=DBNCommandDefinitionNode)
    
    def test_complain_no_args(self):
        """
        it should throw an error if no args are passed
        """
        tokens = self.make_tokens(
            ('COMMAND', ''),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_define_command, tokens, expected=DBNCommandDefinitionNode)
        
    def test_complain_non_word_arg(self):
        """
        will complain if any of the args is not a word
        """
        """
        tests a noarg command defind
        """
        tokens = self.make_tokens(
            ('COMMAND', ''),
            ('WORD', 'Ploop'),
            ('WORD', 'X'),
            ('NUMBER', '9'),
            ('WORD', 'L'),
            ('WORD', 'R'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_define_command, tokens, expected=DBNCommandDefinitionNode)
    


if __name__ == "__main__":
    unittest.main()
