import sys

from . import structures
from . import adapters

DEFAULT_VARIABLE_VALUE = 0
DEFAULT_INITIAL_PAPER_COLOR = 0
DEFAULT_INITIAL_PEN_COLOR = 100

import time


class DBNInterpreter:

    def __init__(self, bytecode):
        self.bytecode = bytecode

        self.commands = {}
        self.numbers = {}

        # the adpater bus to the external world
        self.adapter_bus = structures.AdapterBus()
        self.adapter_bus.connect(self)

        loader = adapters.LoadAdapter()
        self.adapter_bus.attach(loader)

        self.image = structures.DBNImage(DEFAULT_INITIAL_PAPER_COLOR)
        self.pen_color = DEFAULT_INITIAL_PEN_COLOR

        # initialize base frame
        base_frame = structures.DBNFrame()
        self.set_frame(base_frame)

        # line no
        self.line_no = -1

        # program count
        self.pointer = 0

        # status
        self.terminated = False

    ####
    # The module loading methods

    def load(self, module):
        """
        looks for attributes in passed module
         - COMMANDS, adds them to the proper place
        """
        try:
            commands = module.COMMANDS
        except AttributeError:
            pass
        else:
            self._load_commands(commands)

        try:
            numbers = module.NUMBERS
        except AttributeError:
            pass
        else:
            self._load_numbers(numbers)

    def _load_commands(self, commands):
        for command_klass in commands:
            command = command_klass()
            self.store_proc('command', command)

    def _load_numbers(self, numbers):
        for number_klass in numbers:
            number = number_klass()
            self.store_proc('number', number)

    ####
    # The procedure access methods
    def _get_proc_table(self, proc_type):
        if proc_type == 'number':
            return self.numbers
        elif proc_type == 'command':
            return self.commands
        else:
            raise AttributeError('No proc table for proc_type %s' % proc_type)

    def store_proc(self, proc_type, procedure):
        try:
            proc_table = self._get_proc_table(proc_type)
        except AttributeError:
            raise RuntimeError('Unknown proc_type %s!' % proc_type)
        proc_table[procedure.name] = procedure

    def load_proc(self, proc_type, proc_name):
        try:
            proc_table = self._get_proc_table(proc_type)
        except AttributeError:
            raise RuntimeError('Unknown proc_type %s!' % proc_type)
        return proc_table.get(proc_name)

    ####
    # The frame manaagement methods

    def set_frame(self, frame):
        self.frame = frame
        self.stack = frame.stack

    def push_frame(self):
        new_frame = structures.DBNFrame(
            parent=self.frame,
            return_pointer=self.pointer + 1,
            depth = self.frame.depth + 1,
        )
        self.set_frame(new_frame)

    def pop_frame(self):
        old_frame = self.frame.parent
        if old_frame is None:
            raise RuntimeError("Pop frame with no parent")

        self.set_frame(old_frame)

    ####
    # The interpretation methods

    def run(self, **kwargs):
        trace = kwargs.get('trace', False)

        step = self.step
        while not self.terminated:
            code = self.bytecode[self.pointer]
            op, arg = code.op, code.arg

            if trace:
                print(self.pointer, '%s %s' % (op, arg))

            self.step(op, arg)

    def step(self, op, arg):
        op_handler_name = "_op_%s" % op

        try:
            op_handler = getattr(self, op_handler_name)
        except AttributeError:
            raise RuntimeError("Unknown opcode %s" % op)
        else:
            op_handler(arg)

    ####
    # The opcode handlers

    def _op_END(self, arg):
        self.terminated = True

    def _op_SET_LINE_NO(self, arg):
        line_no = int(arg)
        if line_no == -1:
            raise RuntimeError("Why is line_no being set to -1??")
        else:
            self.line_no = line_no
        self.pointer += 1

    def _op_STORE(self, arg):
        val = self.stack.pop()
        self.frame.bind_variable(arg, val)
        self.pointer += 1

    def _op_LOAD(self, arg):
        val = self.frame.lookup_variable(arg, default=DEFAULT_VARIABLE_VALUE)
        self.stack.append(val)
        self.pointer += 1

    def _op_LOAD_INTEGER(self, arg):
        self.stack.append(int(arg))
        self.pointer += 1

    def _op_LOAD_STRING(self, arg):
        self.stack.append(arg)
        self.pointer += 1

    def _op_SET_DOT(self, arg):
        x = self.stack.pop()
        y = self.stack.pop()
        val = self.stack.pop()
        self.image.set_pixel(x, y, val)
        self.pointer += 1

    def _op_GET_DOT(self, arg):
        x = self.stack.pop()
        y = self.stack.pop()
        val = self.image.query_pixel(x, y)
        self.stack.append(val)
        self.pointer += 1

    def _op_BINARY_ADD(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        self.stack.append(top + top1)
        self.pointer += 1

    def _op_BINARY_SUB(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        self.stack.append(top - top1)
        self.pointer += 1

    def _op_BINARY_DIV(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        try:
            self.stack.append(int(top / top1))
        except ZeroDivisionError:
            raise RuntimeError("You can't divide by 0!")
        self.pointer += 1

    def _op_BINARY_MUL(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        self.stack.append(top * top1)
        self.pointer += 1

    def _op_COMPARE_SAME(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        self.stack.append(int(top == top1))
        self.pointer += 1

    def _op_COMPARE_SMALLER(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        self.stack.append(int(top < top1))
        self.pointer += 1

    def _op_DUP_TOPX(self, arg):
        c = int(arg)
        dups = self.stack[-c:]
        self.stack.extend(dups)
        self.pointer += 1

    def _op_POP_TOPX(self, arg):
        c = int(arg)
        for i in range(c):
            self.stack.pop()
        self.pointer += 1

    def _op_ROT_TWO(self, arg):
        top = self.stack.pop()
        top1 = self.stack.pop()
        self.stack.append(top)
        self.stack.append(top1)
        self.pointer += 1

    def _op_JUMP(self, arg):
        target = int(arg)
        self.pointer = target

    def _op_POP_JUMP_IF_FALSE(self, arg):
        target = int(arg)
        top = self.stack.pop()
        if not top:
            self.pointer = target
        else:
            self.pointer += 1

    def _op_POP_JUMP_IF_TRUE(self, arg):
        target = int(arg)
        top = self.stack.pop()
        if top:
            self.pointer = target
        else:
            self.pointer += 1

    def _op_REPEAT_STEP(self, arg):
        top1, top = self.stack[-2:]
        if top == top1:
            # Then we are finished with the repeat
            self.stack[-2:] = [] # pop em
            self.pointer += 1 # and move on
        else:
            direction = 1 if top < top1 else -1
            self.stack[-1] = top + direction
            self.pointer = int(arg)

    def _op_DEFINE_PROCEDURE(self, arg):
        proc_type = self.stack.pop()
        proc_pointer = self.stack.pop()
        proc_name = self.stack.pop()

        argc = int(arg)
        formal_args = [self.stack.pop() for i in range(argc)]

        procedure = structures.DBNUserProcedure(proc_type, proc_name, formal_args, proc_pointer)
        self.store_proc(proc_type, procedure)
        self.pointer += 1

    def _op_PROCEDURE_CALL(self, arg):
        proc_type = self.stack.pop()
        proc_name = self.stack.pop()

        procedure = self.load_proc(proc_type, proc_name)
        if procedure is None:
            raise RuntimeError('No such %s! %s' % (proc_type, proc_name))

        argc = int(arg)
        if not argc == procedure.argc:
            raise RuntimeError('bad argc')

        evaled_args = [self.stack.pop() for i in range(argc)]

        if procedure.is_builtin:
            retval = procedure.call(self, *evaled_args)
            retval = retval if retval is not None else DEFAULT_VARIABLE_VALUE
            self.stack.append(retval)
            self.pointer += 1

        else:
            # push a frame
            self.push_frame()

            # bind the variables
            self.frame.bind_variables(**dict(zip(procedure.formal_args, evaled_args)))

            # jump!
            self.pointer = procedure.body_pointer

    def _op_RETURN(self, arg):
        # return val is TOP
        # TODO error guard / catch
        retval = self.stack.pop()

        # save current rp
        return_location = self.frame.return_pointer

        # restore the frame
        self.pop_frame()

        # and put our retval in
        self.stack.append(retval)

        # and jump!
        self.pointer = return_location

    def _op_LOAD_CODE(self, arg):
        # loaded code is responsible for ensuring we return to the next address
        filename = arg
        offset = len(self.bytecode) # the position of the first bytecode of the foreign code
        return_pos = self.pointer + 1
        compiled_foreign_code = self.adapter_bus.send('loader', 'load', filename, offset, return_pos)

        # we trust that this bytecode has a jump at the end to `return_pos`
        self.bytecode.extend(compiled_foreign_code)

        self.pointer = offset


if __name__ == "__main__":
    import builtins
    import output

    bytecode = []

    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) == 2:
            o, a = parts
        else:
            n, o, a = parts
        bytecode.append((o, a))

    i = DBNInterpreter(bytecode)
    i.load(builtins)
    i.run(trace = True)
    output.draw_window(i)
