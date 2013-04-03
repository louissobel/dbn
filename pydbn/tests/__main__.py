import unittest
import os

test_modules = [
    'tokenizer_tests',
    'parser_tests',
]

for mod in test_modules:
    os.system('python -m tests.%s' % mod)