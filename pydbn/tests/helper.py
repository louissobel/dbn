import unittest
import os
import sys
import subprocess
import StringIO

def run_all_in_dir(file):
    all_tests = unittest.TestLoader().discover(os.path.dirname(file), pattern='*.py')
    r = unittest.TextTestRunner(verbosity=2).run(all_tests)

    if r.failures or r.errors:
        sys.exit(1)

def run_modules(modules, prefix=None):
    for mod in modules:
        if prefix:
            mod = "%s.%s" % (prefix, mod)

        args = ['python', '-m', 'tests.%s' % mod]
        print "Testing %s with \"%s\"...\t" % (mod, ' '.join(args)),
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = proc.communicate()
        ret = proc.returncode

        if ret == 0:
            print "OK"
        else:
            print "FAIL"
