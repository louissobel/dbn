"""
Tests implementation of each opcode
"""
import unittest

from interpreter import DBNInterpreter
from interpreter.interpreter import DEFAULT_VARIABLE_VALUE
from interpreter.structures import commands

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
        interpreter.pointer = pointer

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


class DUP_TOPX_test(InterpreterOpCodeTest):

    OPCODE = 'DUP_TOPX'

    def test_one(self):
        self.fabricate_interpreter(stack=[60])
        self.do_step('1', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[60, 60])

    def test_multiple(self):
        self.fabricate_interpreter(stack=[1, 2, 3, 4, 5])
        self.do_step('3', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[1, 2, 3, 4, 5, 3, 4, 5])


class POP_TOPX_test(InterpreterOpCodeTest):

    OPCODE = 'POP_TOPX'

    def test_one(self):
        self.fabricate_interpreter(stack=[60])
        self.do_step('1', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[])

    def test_multiple(self):
        self.fabricate_interpreter(stack=[1, 2, 3, 4, 5])
        self.do_step('3', expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[1, 2])


class ROT_TWO_test(InterpreterOpCodeTest):

    OPCODE = 'ROT_TWO'

    def runTest(self):
        self.fabricate_interpreter(stack=[1, 2, 3, 4, 5])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[1, 2, 3, 5, 4])


class JUMP_test(InterpreterOpCodeTest):

    OPCODE = 'JUMP'

    def runTest(self):
        loc = 85
        self.fabricate_interpreter()
        self.do_step(str(loc), expected_pointer=loc)


class POP_JUMP_IF_FALSE_test(InterpreterOpCodeTest):

    OPCODE = 'POP_JUMP_IF_FALSE'

    def test_value_is_false(self):
        loc = 9898
        self.fabricate_interpreter(stack=[0])
        self.do_step(str(loc), expected_pointer=loc)
        self.assert_interpreter(stack=[])

    def test_value_is_true(self):
        loc = 9898
        self.fabricate_interpreter(stack=[1])
        self.do_step(str(loc), expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[])


class POP_JUMP_IF_TRUE_test(InterpreterOpCodeTest):

    OPCODE = 'POP_JUMP_IF_TRUE'

    def test_value_is_false(self):
        loc = 9898
        self.fabricate_interpreter(stack=[0])
        self.do_step(str(loc), expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[])

    def test_value_is_true(self):
        loc = 9898
        self.fabricate_interpreter(stack=[1])
        self.do_step(str(loc), expected_pointer=loc)
        self.assert_interpreter(stack=[])


class REPEAT_STEP_test(InterpreterOpCodeTest):

    OPCODE = 'REPEAT_STEP'

    def test_first_is_less(self):
        self.fabricate_interpreter(stack=[90, 50])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[90, 51])

    def test_first_is_more(self):
        self.fabricate_interpreter(stack=[50, 90])
        self.do_step(expected_pointer=INCREMENT)
        self.assert_interpreter(stack=[50, 89])


class DEFINE_COMMAND_test(InterpreterOpCodeTest):

    OPCODE = 'DEFINE_COMMAND'

    def assert_command(self, name, pointer, args=None):
        command = self.interpreter.commands.get(name)
        self.assertIsNotNone(command)
        self.assertEqual(command.name, name)
        self.assertEqual(command.body_pointer, pointer)
        if args:
            self.assertEqual(tuple(command.formal_args), tuple(args))

    def test_no_args(self):
        self.fabricate_interpreter(stack=['bloop', 87])
        self.do_step('0', expected_pointer=INCREMENT)
        self.assert_command('bloop', 87)
        self.assert_interpreter(stack=[])

    def test_with_args(self):
        self.fabricate_interpreter(stack=['C', 'B', 'A', 'bloop', 900])
        self.do_step('2', expected_pointer=INCREMENT)
        self.assert_command('bloop', 900, ['A', 'B'])
        self.assert_interpreter(stack=['C'])


class COMMAND_test(InterpreterOpCodeTest):

    OPCODE = 'COMMAND'

    def create_commands(self):
        """
        builds a fake built in and user command
        """
        user_command = commands.DBNCommand('test', ['A', 'B'], 80)
        user_command_no_args = commands.DBNCommand('testnoargs', [], 876)

        self.builtin_called = False
        class TestBuiltinCommand(commands.DBNBuiltinCommand):

            def __init__(self):
                commands.DBNBuiltinCommand.__init__(self, 0)

            def keyword(self):
                return "test_builtin"

            def call(command, interpreter):
                # tell the test class
                self.builtin_called = True

        self.interpreter.commands['test'] = user_command
        self.interpreter.commands['test_no_args'] = user_command_no_args

        tb = TestBuiltinCommand()
        self.interpreter.commands[tb.keyword()] = tb

    def test_command_call(self):
        """
        Full test of most normal use
        """
        self.fabricate_interpreter(stack=[0, 9, 'test'], pointer=654)
        self.create_commands()

        self.old_frame = self.interpreter.frame
        self.do_step('2', expected_pointer=80)

        # assert the frame
        self.assertIs(self.old_frame, self.interpreter.frame.parent)
        self.assertEqual(self.interpreter.frame.lookup_variable('A'), 9)
        self.assertEqual(self.interpreter.frame.lookup_variable('B'), 0)
        self.assertEqual(self.interpreter.frame.return_pointer, 655)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.old_frame.stack, [])

    def test_command_no_args(self):
        """
        ok
        """
        self.fabricate_interpreter(stack=[0, 9, 'test_no_args'], pointer=6)
        self.create_commands()

        self.old_frame = self.interpreter.frame
        self.do_step('0', expected_pointer=876)

        # assert the frame
        self.assertIs(self.old_frame, self.interpreter.frame.parent)
        self.assertEqual(self.interpreter.frame.return_pointer, 7)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.old_frame.stack, [0, 9])

    def test_builtin_command(self):
        """
        a builtin command should be called
        """
        self.fabricate_interpreter(stack=['test_builtin'])
        self.create_commands()

        self.do_step('0', expected_pointer=INCREMENT)
        self.assertTrue(self.builtin_called)
        self.assert_interpreter(stack=[0])

    def test_not_defined(self):
        """
        runtime if command not defined
        """
        self.fabricate_interpreter(stack=[0, 9, 'nope'])
        self.create_commands()

        with self.assertRaises(RuntimeError):
            self.do_step('3')

    def test_command_bad_argc_user(self):
        """
        a user command called with bad argc should throw error
        """
        self.fabricate_interpreter(stack=[0, 9, 'test'])
        self.create_commands()

        with self.assertRaises(RuntimeError):
            self.do_step('8')

    def test_command_bad_argc_builtin(self):
        """
        a builtin command called with bad argc should throw error
        """
        self.fabricate_interpreter(stack=['test_builtin'])
        self.create_commands()

        with self.assertRaises(RuntimeError):
            self.do_step('8')


# RETURN
# LOAD_CODE

if __name__ == "__main__":
    unittest.main()
