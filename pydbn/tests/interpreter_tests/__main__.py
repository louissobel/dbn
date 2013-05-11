import unittest
import os
import sys

all_tests = unittest.TestLoader().discover(os.path.dirname(__file__), pattern='*.py')
r = unittest.TextTestRunner(verbosity=2).run(all_tests)

if r.failures or r.errors:
    sys.exit(1)