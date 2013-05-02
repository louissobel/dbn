import unittest

import interpreter

import _opcodes

class BinaryAdd(unittest.TestCase):

    def runTest(self):
        interp = interpreter.DBNInterpreter([])
        interp.stack = [1,2,3,4]

        _opcodes._op_BINARY_ADD(interp, '_')
        
        self.assertEqual([1,2,7], interp.stack)
        self.assertEqual(1, interp.pointer)


if __name__ == "__main__":
    unittest.main()
        