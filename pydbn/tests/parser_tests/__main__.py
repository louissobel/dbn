import unittest
import os

all_tests = unittest.TestLoader().discover(os.path.dirname(__file__), pattern='*.py')
unittest.TextTestRunner(verbosity=2).run(all_tests)