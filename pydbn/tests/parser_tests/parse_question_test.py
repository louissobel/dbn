import random
import unittest

import parser
from parser.structures.ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase


class ParseQuestionTest(ParserTestCase):
    """
    parses a question
    """

    def assert_question_node(self, node, value, arg_types):
        """
        checks that arg_types match the args
        and that the third child is a body
        """
        self.assertEquals(value, node.value)
        
        self.assertEquals(3, len(node.children))
        
        for type_, child in zip(arg_types, node.children[0:2]):
            self.assertIsInstance(child, type_)
        
        self.assertIsInstance(node.children[2], DBNBlockNode)

    def test_question(self):
        """
        tests a basic question parse works
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('QUESTION', 'Same?'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('NEWLINE', '\n'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )
        result, result_tokens = self.run_parse(parser.parse_question, tokens, expected=DBNQuestionNode, line_no=line_no)
        self.assert_question_node(result, 'Same?', (DBNNumberNode, DBNNumberNode))
    
    def test_question_sameline_brace(self):
        """
        tests a basic question parse works with the leading body brace on the same line
        """
        tokens = self.make_tokens(
            ('QUESTION', 'Same?'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', '\n'),
        )
        result, result_tokens = self.run_parse(parser.parse_question, tokens, expected=DBNQuestionNode)
        self.assert_question_node(result, 'Same?', (DBNNumberNode, DBNNumberNode))
    
    def test_question_no_newline(self):
        """
        tests that an unterminated question will raise ValueError
        """
        tokens = self.make_tokens(
            ('QUESTION', 'Same?'),
            ('NUMBER', '0'),
            ('NUMBER', '0'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            # now some other token
            ('SET', ''),
        )
        
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_question, tokens, expected=DBNQuestionNode)


if __name__ == "__main__":
    unittest.main()
