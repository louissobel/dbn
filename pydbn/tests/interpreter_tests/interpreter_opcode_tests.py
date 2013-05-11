"""
Tests implementation of each opcode
"""
import unittest

from interpreter import DBNInterpreter
from interpreter.interpreter import DEFAULT_VARIABLE_VALUE

# enum
INCREMENT = -432

class InterpreterOpCodeTest(unittest.TestCase):

    @property
    def OPCODE(self):
        raise NotImplementedError

    def fabricate_interpreter(self, stack=None, pointer=0, env=None):
        """
        sweet
        """
        # no bytecode
        interpreter = DBNInterpreter([])

        # mess with the base frame
        frame = interpreter.frame

        frame.stack = stack or []
        frame.env = env or frame.env

        # re-set the frame
        interpreter.set_frame(frame)

        self.interpreter = interpreter
        return interpreter

    def do_step(self, arg='_', expected_pointer=None):
        self.__last_pointer_val = self.interpreter.pointer
        self.interpreter.step(self.OPCODE, arg)
        if expected_pointer is not None:
            if expected_pointer == INCREMENT:
                self.assertEquals(self.__last_pointer_val + 1, self.interpreter.pointer)
            else:
                self.assertEquals(expected_pointer, self.interpreter.pointer)

    def assert_interpreter(self, stack=None):
        if stack is not None:
            self.assertEquals(stack, self.interpreter.stack)


class END_test(InterpreterOpCodeTest):

    OPCODE = 'END'

    def runTest(self):
        self.fabricate_interpreter()
        self.do_step()
        self.assertTrue(self.interpreter.terminated)


class SET_LINE_NO_test(InterpreterOpCodeTest):

    OPCODE = 'SET_LINE_NO'

    def test_normal(self):
        self.fabricate_interpreter()
        self.do_step('9', expected_pointer=INCREMENT)
        self.assertEquals(self.interpreter.line_no, 9)

    def test_error(self):
        self.fabricate_interpreter()

        with self.assertRaises(RuntimeError):
            self.do_step('-1')


class STORE_test(InterpreterOpCodeTest):

    OPCODE = 'STORE'

    def runTest(self):
        self.fabricate_interpreter(stack=[908])
        self.do_step('a', expected_pointer=INCREMENT)
        self.assertEquals(908, self.interpreter.frame.lookup_variable('a'))

        # Pop the value
        self.assert_interpreter(stack=[])


class LOAD_test(InterpreterOpCodeTest):

    OPCODE = 'LOAD'

    def test_variable_defined(self):
        self.fabricate_interpreter(stack=[], env={'a' : 800})
        self.do_step('a', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[800])

    def test_variable_not_defined(self):
        self.fabricate_interpreter(stack=[], env={'a' : 800})
        self.do_step('b')
        self.assert_interpreter(stack=[DEFAULT_VARIABLE_VALUE])


class LOAD_INTEGER_test(InterpreterOpCodeTest):

    OPCODE = 'LOAD_INTEGER'

    def runTest(self):
        self.fabricate_interpreter(stack=[])
        self.do_step('800', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[800])


class LOAD_STRING_test(InterpreterOpCodeTest):

    OPCODE = 'LOAD_STRING'

    def runTest(self):
        self.fabricate_interpreter(stack=[])
        self.do_step('hi', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=['hi'])


class SET_DOT_test(InterpreterOpCodeTest):

    OPCODE = 'SET_DOT'

    def test_in_bounds(self):
        self.fabricate_interpreter(stack=[50, 70, 30])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.interpreter.image.query_pixel(30, 70), 50)

    def test_out_of_bounds(self):
        # then it should just silently not do anything
        self.fabricate_interpreter(stack=[50, 1000, 1000])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[])

    def test_boundaries(self):
        self.fabricate_interpreter(stack=[-489, 100, 100])
        self.do_step()
        self.assertEqual(self.interpreter.image.query_pixel(100, 100), 0)

        self.fabricate_interpreter(stack=[1000, 0, 0])
        self.do_step()
        self.assertEqual(self.interpreter.image.query_pixel(0, 0), 100)


class GET_DOT_test(InterpreterOpCodeTest):

    OPCODE = 'GET_DOT'

    def test_in_bounds(self):
        c = 87
        self.fabricate_interpreter(stack=[30, 70])
        self.interpreter.image.set_pixel(70, 30, c)
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[c])

    def test_out_of_bounds(self):
        self.fabricate_interpreter(stack=[1000, 1000])
        self.do_step()
        self.assert_interpreter(stack=[DEFAULT_VARIABLE_VALUE])


class BINARY_ADD_test(InterpreterOpCodeTest):

    OPCODE = 'BINARY_ADD'

    def runTest(self):
        self.fabricate_interpreter(stack=[40, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[50 + 40])


class BINARY_SUB_test(InterpreterOpCodeTest):

    OPCODE = 'BINARY_SUB'

    def test_positive_result(self):
        self.fabricate_interpreter(stack=[40, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[50 - 40])

    def test_positive_result(self):
        self.fabricate_interpreter(stack=[50, 40])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[40 - 50])


class BINARY_MUL_test(InterpreterOpCodeTest):

    OPCODE = 'BINARY_MUL'

    def runTest(self):
        self.fabricate_interpreter(stack=[40, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[40 * 50])


class BINARY_DIV_test(InterpreterOpCodeTest):

    OPCODE = 'BINARY_DIV'

    def test_no_remainder(self):
        self.fabricate_interpreter(stack=[10, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[50 / 10])

    def test_floor_division(self):
        """
        we do floor division
        """
        self.fabricate_interpreter(stack=[12, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[50 / 12]) # 4

    def test_divide_by_0(self):
        """
        uh oh
        """
        self.fabricate_interpreter(stack=[0, 80])
        with self.assertRaises(RuntimeError):
            self.do_step()


class COMPARE_SAME_test(InterpreterOpCodeTest):

    OPCODE = 'COMPARE_SAME'

    def test_they_are_the_same(self):
        self.fabricate_interpreter(stack=[50, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[1])

    def test_they_are_not_the_same(self):
        self.fabricate_interpreter(stack=[45, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[0])


class COMPARE_SMALLER_test(InterpreterOpCodeTest):

    OPCODE = 'COMPARE_SMALLER'

    def test_first_is_smaller(self):
        self.fabricate_interpreter(stack=[50, 30])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[1])

    def test_first_is_not_smaller(self):
        self.fabricate_interpreter(stack=[30, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[0])

# DUP_TOPX
# POP_TOPX
# ROT_TWO
# JUMP
# POP_JUMP_IF_FALSE
# POP_JUMP_IF_TRUE
# REPEAT_STEP
# DEFINE_COMMAND
# COMMAND
# RETURN
# LOAD_CODE

if __name__ == "__main__":
    unittest.main()
