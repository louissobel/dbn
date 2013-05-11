import unittest

from parser.structures import DBNToken

class ParserTestCase(unittest.TestCase):

    def make_tokens(self, *type_value_pairs, **kwargs):
        return [DBNToken(type_, value, kwargs.get('line_no', 0), 0, '') for type_, value in type_value_pairs]

    def run_parse(self, parse_function, tokens, **kwargs):
        """
        dups the tokens and passes them to the parse function
        returns the result of the parse function and the duped,
        potentially mutated, token list
        """
        input_tokens = tokens[:]
        result = parse_function(input_tokens)
        
        if 'expected' in kwargs:
            expected_type = kwargs['expected']
            self.assertIsInstance(result, expected_type)
        
        if 'line_no' in kwargs:
            self.assertEquals(kwargs['line_no'], result.line_no)

        # defult to asserting input tokens is empty
        if kwargs.get('assert_empty', True):
            self.assertEqual(0, len(input_tokens))
        
        # default to asserting that the nodes tokens matches the passed token list
        if kwargs.get('assert_token_match', True):
            self.assertEqual(tokens, result.tokens)

        return result, input_tokens