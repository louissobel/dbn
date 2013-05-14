"""
Tests implementation of each opcode
"""
import unittest

from interpreter import DBNInterpreter
from interpreter.interpreter import DEFAULT_VARIABLE_VALUE
from interpreter.structures import commands
from interpreter.adapters import BaseAdapter

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


class DEFINE_PROCEDURE_test(InterpreterOpCodeTest):

    OPCODE = 'DEFINE_PROCEDURE'

    def assert_procedure(self, type_, name, pointer, args=None):
        if type_ == 'number':
            proctable = self.interpreter.numbers
        elif type_ == 'command':
            proctable = self.interpreter.commands
        proc = proctable.get(name)
        self.assertIsNotNone(proc)
        self.assertEqual(proc.name, name)
        self.assertEqual(proc.body_pointer, pointer)
        if args:
            self.assertEqual(tuple(proc.formal_args), tuple(args))

    def test_no_args_command(self):
        self.fabricate_interpreter(stack=['bloop', 87, 'command'])
        self.do_step('0', expected_pointer=INCREMENT)
        self.assert_procedure('command', 'bloop', 87)
        self.assert_interpreter(stack=[])

    def test_no_args_number(self):
        self.fabricate_interpreter(stack=['bloop', 87, 'number'])
        self.do_step('0', expected_pointer=INCREMENT)
        self.assert_procedure('number', 'bloop', 87)
        self.assert_interpreter(stack=[])

    def test_with_args_command(self):
        self.fabricate_interpreter(stack=['C', 'B', 'A', 'bloop', 900, 'command'])
        self.do_step('2', expected_pointer=INCREMENT)
        self.assert_procedure('command', 'bloop', 900, ['A', 'B'])
        self.assert_interpreter(stack=['C'])

    def test_with_args_number(self):
        self.fabricate_interpreter(stack=['C', 'B', 'A', 'bloop', 900, 'number'])
        self.do_step('2', expected_pointer=INCREMENT)
        self.assert_procedure('number', 'bloop', 900, ['A', 'B'])
        self.assert_interpreter(stack=['C'])


class PROCEDURE_CALL_test(InterpreterOpCodeTest):

    OPCODE = 'PROCEDURE_CALL'

    def create_procedures(self):
        """
        builds a fake built in and user command
        """
        user_command = commands.DBNUserProcedure('command', 'test', ['A', 'B'], 80)
        user_command_no_args = commands.DBNUserProcedure('command', 'test_no_args', [], 876)
        user_number = commands.DBNUserProcedure('number', 'test', ['A', 'B', 'C'], 8000)
        user_number_no_args = commands.DBNUserProcedure('number', 'test_no_args', [], 43)

        self.builtin_called = False
        class TestBuiltinProcedureReturnNone(commands.DBNBuiltinProcedure):

            def __init__(self):
                commands.DBNBuiltinProcedure.__init__(self, 0)

            name = "test_builtin_no_retval"

            def call(command, interpreter):
                # tell the test class
                self.builtin_called = True

        self.builtin_called = False
        class TestBuiltinProcedureReturnValue(commands.DBNBuiltinProcedure):

            def __init__(self):
                commands.DBNBuiltinProcedure.__init__(self, 0)

            name = "test_builtin_retval"

            def call(command, interpreter):
                # tell the test class
                self.builtin_called = True
                return 5

        self.interpreter.store_proc('command', user_command)
        self.interpreter.store_proc('command', user_command_no_args)
        self.interpreter.store_proc('number', user_number)
        self.interpreter.store_proc('number', user_number_no_args)

        self.interpreter._load_commands([TestBuiltinProcedureReturnNone, TestBuiltinProcedureReturnValue])
        self.interpreter._load_numbers([TestBuiltinProcedureReturnNone, TestBuiltinProcedureReturnValue])

    def test_command_call(self):
        """
        Full test of most normal use
        """
        self.fabricate_interpreter(stack=[0, 9, 'test', 'command'], pointer=654)
        self.create_procedures()

        self.old_frame = self.interpreter.frame
        self.do_step('2', expected_pointer=80)

        # assert the frame
        self.assertIs(self.old_frame, self.interpreter.frame.parent)
        self.assertEqual(self.interpreter.frame.lookup_variable('A'), 9)
        self.assertEqual(self.interpreter.frame.lookup_variable('B'), 0)
        self.assertEqual(self.interpreter.frame.return_pointer, 655)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.old_frame.stack, [])
    
    def test_number_call(self):
        """
        Full test of most normal use
        """
        self.fabricate_interpreter(stack=[43, 23, 0, 9, 'test', 'number'], pointer=654)
        self.create_procedures()

        self.old_frame = self.interpreter.frame
        self.do_step('3', expected_pointer=8000)

        # assert the frame
        self.assertIs(self.old_frame, self.interpreter.frame.parent)
        self.assertEqual(self.interpreter.frame.lookup_variable('A'), 9)
        self.assertEqual(self.interpreter.frame.lookup_variable('B'), 0)
        self.assertEqual(self.interpreter.frame.lookup_variable('C'), 23)
        self.assertEqual(self.interpreter.frame.return_pointer, 655)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.old_frame.stack, [43])

    def test_command_no_args(self):
        """
        ok
        """
        self.fabricate_interpreter(stack=[0, 9, 'test_no_args', 'command'], pointer=6)
        self.create_procedures()

        self.old_frame = self.interpreter.frame
        self.do_step('0', expected_pointer=876)

        # assert the frame
        self.assertIs(self.old_frame, self.interpreter.frame.parent)
        self.assertEqual(self.interpreter.frame.return_pointer, 7)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.old_frame.stack, [0, 9])

    def test_number_no_args(self):
        """
        ok
        """
        self.fabricate_interpreter(stack=[0, 9, 'test_no_args', 'number'], pointer=60)
        self.create_procedures()

        self.old_frame = self.interpreter.frame
        self.do_step('0', expected_pointer=43)

        # assert the frame
        self.assertIs(self.old_frame, self.interpreter.frame.parent)
        self.assertEqual(self.interpreter.frame.return_pointer, 61)
        self.assert_interpreter(stack=[])
        self.assertEqual(self.old_frame.stack, [0, 9])

    def test_builtin_command_no_retval(self):
        """
        a builtin number should be called - DEFAULT_VARIABLE_VALUE returned if no retval
        """
        self.fabricate_interpreter(stack=['test_builtin_no_retval', 'command'])
        self.create_procedures()

        self.do_step('0', expected_pointer=INCREMENT)
        self.assertTrue(self.builtin_called)
        self.assert_interpreter(stack=[DEFAULT_VARIABLE_VALUE])

    def test_builtin_number_no_retval(self):
        """
        a builtin number should be called - DEFAULT_VARIABLE_VALUE returned if no retval
        """
        self.fabricate_interpreter(stack=['test_builtin_no_retval', 'number'])
        self.create_procedures()

        self.do_step('0', expected_pointer=INCREMENT)
        self.assertTrue(self.builtin_called)
        self.assert_interpreter(stack=[DEFAULT_VARIABLE_VALUE])

    def test_builtin_command_retval(self):
        """
        a builtin command should be called - its retval pushed on
        """
        self.fabricate_interpreter(stack=['test_builtin_retval', 'command'])
        self.create_procedures()

        self.do_step('0', expected_pointer=INCREMENT)
        self.assertTrue(self.builtin_called)
        self.assert_interpreter(stack=[5])

    def test_builtin_number_retval(self):
        """
        a builtin command should be called
        """
        self.fabricate_interpreter(stack=['test_builtin_retval', 'number'])
        self.create_procedures()

        self.do_step('0', expected_pointer=INCREMENT)
        self.assertTrue(self.builtin_called)
        self.assert_interpreter(stack=[5])

    def test_command_not_defined(self):
        """
        runtime if command not defined
        """
        self.fabricate_interpreter(stack=[0, 9, 'nope', 'command'])
        self.create_procedures()

        with self.assertRaises(RuntimeError):
            self.do_step('2')

    def test_number_not_defined(self):
        """
        runtime if number not defined
        """
        self.fabricate_interpreter(stack=[0, 9, 'nope', 'number'])
        self.create_procedures()

        with self.assertRaises(RuntimeError):
            self.do_step('2')

    def test_command_bad_argc_user(self):
        """
        a user command called with bad argc should throw error
        """
        self.fabricate_interpreter(stack=[0, 9, 'test', 'command'])
        self.create_procedures()

        with self.assertRaises(RuntimeError):
            self.do_step('8')

    def test_number_bad_argc_user(self):
        """
        a user command called with bad argc should throw error
        """
        self.fabricate_interpreter(stack=[0, 9, 'test', 'number'])
        self.create_procedures()

        with self.assertRaises(RuntimeError):
            self.do_step('8')

    def test_command_bad_argc_builtin(self):
        """
        a builtin command called with bad argc should throw error
        """
        self.fabricate_interpreter(stack=['test_builtin_retval', 'command'])
        self.create_procedures()

        with self.assertRaises(RuntimeError):
            self.do_step('8')

    def test_number_bad_argc_builtin(self):
        """
        a builtin command called with bad argc should throw error
        """
        self.fabricate_interpreter(stack=['test_builtin_retval', 'number'])
        self.create_procedures()

        with self.assertRaises(RuntimeError):
            self.do_step('8')


class RETURN_test(InterpreterOpCodeTest):

    OPCODE = 'RETURN'

    def test_stack_not_empty(self):
        """
        Normal operation
        """
        self.fabricate_interpreter(stack=[], pointer=80)
        old_frame = self.interpreter.frame
        self.interpreter.push_frame()

        self.interpreter.stack.append(7)
        self.interpreter.pointer = 80982
        self.do_step(expected_pointer=81) # one after where we pushed the frame

        self.assertIs(self.interpreter.frame, old_frame)
        self.assert_interpreter(stack=[7])

    def test_stack_empty(self):
        """
        unexpected return
        """
        self.fabricate_interpreter(stack=[3])
        with self.assertRaises(RuntimeError):
            self.do_step()


class LOAD_CODE_test(InterpreterOpCodeTest):

    OPCODE = 'LOAD_CODE'

    def runTest(self):

        class MockLoader(BaseAdapter):
            def identifier(self):
                return 'loader'
            def load(self, *args):
                return [1, 3, 5]

        self.fabricate_interpreter()
        self.interpreter.adapter_bus.attach(MockLoader())

        self.interpreter.bytecode = [0, 2, 4]

        self.do_step('foo', expected_pointer=3) # the index after current bytecode
        self.assertEqual(self.interpreter.bytecode, [0, 2, 4, 1, 3, 5])


if __name__ == "__main__":
    unittest.main()
