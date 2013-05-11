import unittest

import parser
from parser.structures.ast_nodes import *
from tests.unit_tests.parser_tests.base_test import ParserTestCase


class ParseArithmeticTest(ParserTestCase):
    """
    Lots of test cases for the part that poarses ops
    """
    OPERATORS = ['+', '-', '*', '/']
    
    
    def assert_binary_op(self, binop, operator, childs):        
        self.assertEquals(len(binop.children), 2)
        self.assertEquals(binop.value, operator)
        for type_, node in zip(childs, binop.children):
            self.assertIsInstance(node, type_)
    
    def test_simple_arg(self):
        """
        parse_aritmetic should parse a single element
        """
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '0'),
            ('CLOSEPAREN', ''),
        )
        result, result_tokens = self.run_parse(parser.parse_arithmetic, tokens, expected=DBNNumberNode)
        
        # check that the paren tokens are there
        self.assertEqual(tokens, result.tokens)
    
    def test_binary_op(self):
        """
        parse_arithmetic should parse binary ops for every operator
        """
        for operator in self.OPERATORS:
            
            tokens = self.make_tokens(
                ('OPENPAREN', ''),
                ('NUMBER', '3'),
                ('OPERATOR', operator),
                ('NUMBER', '2'),
                ('CLOSEPAREN', ''),
            )
            result, result_tokens = self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)

            self.assert_binary_op(result, operator, (DBNNumberNode, DBNNumberNode))
            self.assertEquals('3', result.children[0].value)
            self.assertEquals('2', result.children[1].value)


    def test_left_associativity(self):
        """
        all operators should associate left
        """
        for operator in self.OPERATORS:
            
            # ( 1 + 2 + 3)
            tokens = self.make_tokens(
                ('OPENPAREN', ''),
                ('NUMBER', '1'),
                ('OPERATOR', operator),
                ('NUMBER', '2'),
                ('OPERATOR', operator),
                ('NUMBER', '3'),
                ('CLOSEPAREN', '')
            )
            
            result, result_tokens = self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)

            self.assert_binary_op(result, operator, (DBNBinaryOpNode, DBNNumberNode))
            self.assertEquals('3', result.children[1].value)

            left_child = result.children[0]
            self.assert_binary_op(left_child, operator, (DBNNumberNode, DBNNumberNode))
            self.assertEquals('1', left_child.children[0].value)
            self.assertEquals('2', left_child.children[1].value)
    
    def test_mixed_precedence(self):
        """
        a simple mixed precedence parse
        """
        # ( 1 + 2 * 3)
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '1'),
            ('OPERATOR', '+'),
            ('NUMBER', '2'),
            ('OPERATOR', '*'),
            ('NUMBER', '3'),
            ('CLOSEPAREN', '')
        )
        
        result, result_tokens = self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)

        self.assert_binary_op(result, '+', (DBNNumberNode, DBNBinaryOpNode))
        self.assertEquals('1', result.children[0].value)

        right_child = result.children[1]
        self.assert_binary_op(right_child, '*', (DBNNumberNode, DBNNumberNode))
        self.assertEquals('2', right_child.children[0].value)
        self.assertEquals('3', right_child.children[1].value)

    def test_complex_mixed_precedence(self):
        """
        a more complicated mixed precedence
        """
        # (1 + 2 * 3 - 4 / 5) ---> ((1 + (2 * 3)) - (4 / 5))
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '1'),
            ('OPERATOR', '+'),
            ('NUMBER', '2'),
            ('OPERATOR', '*'),
            ('NUMBER', '3'),
            ('OPERATOR', '-'),
            ('NUMBER', '4'),
            ('OPERATOR', '/'),
            ('NUMBER', '5'),
            ('CLOSEPAREN', '')
        )
        result, result_tokens = self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)

        self.assert_binary_op(result, '-', (DBNBinaryOpNode, DBNBinaryOpNode))
        plus_op = result.children[0]
        div_op = result.children[1]

        self.assert_binary_op(plus_op, '+', (DBNNumberNode, DBNBinaryOpNode))
        self.assertEquals(plus_op.children[0].value, '1')
        mul_op = plus_op.children[1]

        self.assert_binary_op(mul_op, '*', (DBNNumberNode, DBNNumberNode))
        self.assertEquals('2', mul_op.children[0].value)
        self.assertEquals('3', mul_op.children[1].value)

        self.assert_binary_op(div_op, '/', (DBNNumberNode, DBNNumberNode))
        self.assertEquals('4', div_op.children[0].value)
        self.assertEquals('5', div_op.children[1].value)

    def test_double_operator_error(self):
        """
        it should throw an error if two operators are next
        to eachother
        """
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '3'),
            ('OPERATOR', '+'),
            ('OPERATOR', '+'),
            ('NUMBER', '2'),
            ('CLOSEPAREN', ''),
        )
        
        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)
    
    def test_leading_operator_error(self):
        """
        it should throw an error if an operator leads
        """
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('OPERATOR', '+'),
            ('NUMBER', '2'),
            ('CLOSEPAREN', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)
            
    def test_trailing_operator_error(self):
        """
        it should throw an error if an operator trails
        """
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '2'),
            ('OPERATOR', '+'),
            ('CLOSEPAREN', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)
    
    def test_double_number_error(self):
        """
        it should throw an error if an operator trails
        """
        tokens = self.make_tokens(
            ('OPENPAREN', ''),
            ('NUMBER', '2'),
            ('NUMBER', '2'),
            ('CLOSEPAREN', ''),
        )

        with self.assertRaises(ValueError):
            self.run_parse(parser.parse_arithmetic, tokens, expected=DBNBinaryOpNode)


if __name__ == "__main__":
    unittest.main()
