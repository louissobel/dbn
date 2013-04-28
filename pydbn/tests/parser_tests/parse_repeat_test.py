import random
import unittest

import parser
from ast_nodes import *
from tests.parser_tests.base_test import ParserTestCase


class ParseRepeatTest(ParserTestCase):
    """
    parses a repeat
    """
    def assert_repeat_node(self, node, name, arg_types):
        """
        checks that arg_types match the args
        and that the third child is a body
        """
        self.assertEquals(4, len(node.children))

        self.assertIsInstance(node.children[0], DBNWordNode)
        self.assertEquals(name, node.children[0].name)
        for type_, child in zip(arg_types, node.children[1:3]):
            self.assertIsInstance(child, type_)

        self.assertIsInstance(node.children[3], DBNBlockNode)

    def test_repeat(self):
        """
        tests a basic repeat parse works
        """
        line_no = random.randint(0, 10)
        tokens = self.make_tokens(
            ('REPEAT', ''),
            ('WORD', 'A'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('NEWLINE', '\n'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', '\n'),
            line_no = line_no,
        )
        result, result_tokens = self.run_parse(parser.parse_repeat, tokens, expected=DBNRepeatNode, line_no=line_no)
        self.assert_repeat_node(result, 'A', (DBNNumberNode, DBNNumberNode))
    
    def test_repeat_sameline_brace(self):
        """
        tests a basic repeat parse works with body starting on same line
        """
        tokens = self.make_tokens(
            ('REPEAT', ''),
            ('WORD', 'A'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', '\n'),
        )
        result, result_tokens = self.run_parse(parser.parse_repeat, tokens, expected=DBNRepeatNode)
        self.assert_repeat_node(result, 'A', (DBNNumberNode, DBNNumberNode))

    def test_non_word_variable_error(self):
        """
        ensure that if the first variable isn't a word an error will be thrown
        """
        tokens = self.make_tokens(
            ('REPEAT', ''),
            ('NUMBER', '9'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            ('NEWLINE', '\n'),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_repeat, tokens, expected=DBNRepeatNode)

    def test_repeat_no_newline(self):
        """
        tests that an unterminated repeat will raise ValueError
        """
        tokens = self.make_tokens(
            ('REPEAT', ''),
            ('WORD', 'A'),
            ('NUMBER', '0'),
            ('NUMBER', '100'),
            ('OPENBRACE', ''),
            ('NEWLINE', ''),
            ('CLOSEBRACE', ''),
            # now some other token
            ('SET', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_repeat, tokens, expected=DBNQuestionNode)


if __name__ == "__main__":
    unittest.main()
