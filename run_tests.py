from tests import *
import unittest


suite = unittest.TestLoader().loadTestsFromModule(tokenizer_tests)

runner = unittest.TextTestRunner(verbosity=2)

runner.run(suite)


suite = unittest.TestLoader().loadTestsFromModule(parser_tests)
runner.run(suite)



