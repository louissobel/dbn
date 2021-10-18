# Add the directory of this file to the python search path
# for imports
import os.path
import sys
sys.path.insert(0, os.path.dirname(__file__))

import parser
import compiler
import interpreter
import evm_compiler