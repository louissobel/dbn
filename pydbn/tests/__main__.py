import unittest
import os
import subprocess
import StringIO

test_modules = [
    'tokenizer_tests',
    'parser_tests',
    'integration_tests',
    'load_adapter_tests',
]

for mod in test_modules:
    args = ['python', '-m', 'tests.%s' % mod]
    print "Testing %s with \"%s\"...\t" % (mod, ' '.join(args)),
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = proc.communicate()
    ret = proc.returncode

    if ret == 0:
        print "OK"
    else:
        print "FAIL"
