import unittest
import os
import sys
import subprocess
import StringIO

def run_all_in_dir(file):
    all_tests = unittest.TestLoader().discover(os.path.dirname(file), pattern='*.py')
    r = unittest.TextTestRunner(verbosity=1).run(all_tests)

    if r.failures or r.errors:
        sys.exit(1)

def run_modules(modules, prefix=None, verbose=True):
    failed = False
    for mod in modules:
        if prefix:
            mod = "%s.%s" % (prefix, mod)

        args = ['python', '-m', 'tests.%s' % mod]
        print "Testing %s with \"%s\"...\t" % (mod, ' '.join(args)),

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = proc.communicate()
        ret = proc.returncode

        if verbose:
            print
            print "\n".join("\t%s" % line for line in out.split('\n'))

        if ret == 0:
            print "\033[32mOK\033[0m"
        else:
            failed = True
            print "\033[31mFAIL\033[0m"

    if failed:
        sys.exit(1)
