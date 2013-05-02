import unittest

from interpreter import DBNInterpreter

# The C one
import _opcodes

class OpcodeTestCase():
    """
    base class for opcode test cases
    """
    def stubInterpreter(self):
        """
        do some default stubbing
        """
        self.interpreter.stack = [1, 2, 3, 4, 5, 6]
        self.interpreter.pointer = 0

    def setUp(self):
        self.interpreter = DBNInterpreter([])
        self.stubInterpreter()

    def assertOpcode(self, func):
        pass

    def runTest(self):
        op_handler = "_op_%s" % self.OPCODE

        # test the python one'
        self.assertOpcode(getattr(DBNInterpreter, op_handler))

        # Refresh
        self.setUp()

        # test the C one
        self.assertOpcode(getattr(_opcodes, op_handler))


class TestEnd(OpcodeTestCase, unittest.TestCase):
    OPCODE = 'END'

    def assertOpcode(self, func):
        func(self.interpreter, '_')
        self.assertTrue(self.interpreter.terminated)

class BinaryAdd(OpcodeTestCase, unittest.TestCase):
    OPCODE = 'BINARY_ADD'

    def assertOpcode(self, func):
        func(self.interpreter, '_')
        self.assertEquals([1,2,3,4,11], self.interpreter.stack)
        self.assertEquals(1, self.interpreter.pointer)

class BinaryAddRuntime(OpcodeTestCase, unittest.TestCase):
    OPCODE = 'BINARY_ADD'

    def stubInterpreter(self):
        self.interpreter.stack = [1]

    def assertOpcode(self, func):
        with self.assertRaises((RuntimeError, IndexError)):
            func(self.interpreter, '_')


if __name__ == "__main__":
    unittest.main()
