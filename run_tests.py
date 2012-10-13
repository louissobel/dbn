from tests import *
import unittest


suite = unittest.TestLoader().loadTestsFromModule(tokenizer_tests)
unittest.TextTestRunner(verbosity=2).run(suite)




