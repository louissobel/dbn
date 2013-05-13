import unittest

import parser
from parser.structures.ast_nodes import *
from tests.unit_tests.parser_tests.base_test import ParserTestCase

class ParseDefineProcedureTest(ParserTestCase):
    """
    tests the parse_block function
    """
    def assert_define_procedure(self, result, type_, value, argc):
        """
        asserts a define command node
        """
        self.assertEqual(result.value, type_)
        self.assertEqual(result.children[0].value, value)
        self.assertEqual(len(result.children) - 2, argc)
        self.assertIsInstance(result.children[-1], DBNBlockNode)
    
    def test_define_procedure_command(self):
        """
        tests a noarg command define
        """
        tokens = self.make_tokens(
            ('COMMAND', ''),
            ('WORD', 'Square'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
        self.assert_define_procedure(result, 'COMMAND', 'Square', 0)

    def test_define_procedure_number(self):
        """
        tests a noarg number define
        """
        tokens = self.make_tokens(
            ('NUMBER', ''),
            ('WORD', 'Square'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
        self.assert_define_procedure(result, 'NUMBER', 'Square', 0)

    def test_define_procedure_with_args_command(self):
        """
        tests a command define with args
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
        result, result_tokens = self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
        self.assert_define_procedure(result, 'COMMAND', 'Ploop', 4)

    def test_define_procedure_with_args_number(self):
        """
        tests a number define with args
        """
        tokens = self.make_tokens(
            ('NUMBER', ''),
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
        result, result_tokens = self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
        self.assert_define_procedure(result, 'NUMBER', 'Ploop', 4)
        
    def test_define_procedure_no_newline(self):
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
            self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
    
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
            self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
        
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
            self.run_parse(parser.parse_define_procedure, tokens, expected=DBNProcedureDefinitionNode)
    


if __name__ == "__main__":
    unittest.main()
