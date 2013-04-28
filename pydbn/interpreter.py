import sys

import dbnstate
import structures
import adapter_bus

import adapters.loader

DEFAULT_VARIABLE_VALUE = 0
DEFAULT_INITIAL_PAPER_COLOR = 0
DEFAULT_INITIAL_PEN_COLOR = 100

import time



####
# Op code decorators

def increments_pc(fn):
    """
    decorator that will increment the pointer
    """
    def inner(self, *args, **kwargs):
        fn(self, *args, **kwargs)
        self.pointer += 1
    return inner

def pops_top(n):
    """
    returns decorator that calls fn with top n args
    """
    def decorator(fn):
        def inner(self, *args, **kwargs):
            fn(self, *[self.stack.pop() for i in range(n)])
        return inner
    return decorator

class DBNInterpreter:

    def __init__(self, code, debug=False):
        self.bytecode = code

        self.commands = {}
        self.numbers = {}
        
        # the adpater bus to the external world
        self.adapter_bus = adapter_bus.AdapterBus()
        self.adapter_bus.connect(self)
        
        loader = adapters.loader.LoadAdapter()
        self.adapter_bus.attach(loader)
        
        self.image = dbnstate.DBNImage(DEFAULT_INITIAL_PAPER_COLOR)
        self.pen_color = DEFAULT_INITIAL_PEN_COLOR

        # initialize base frame
        base_frame = dbnstate.DBNFrame()
        self.set_frame(base_frame)

        # line no
        self.line_no = -1

        # program count
        self.pointer = 0
        
        self._DEBUG = debug

    ####
    # The debug methods

    def debug(self, msg):
        if self._DEBUG:
            print msg

    def dump_bytecode(self):
        """
        for debug - dumps bytecode
        """
        out = "------Bytecode:"
        for n, (o, a) in enumerate(self.bytecode):
            out += "%s %s %s" % (n, o, a)
        out += "--------"
        return out

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
            for command_klass in commands:
                command = command_klass()
                self.commands[command.keyword()] = command

    ####
    # The frame manaagement methods

    def set_frame(self, frame):
        self.frame = frame
        self.stack = frame.stack
        self.env = frame.env

    def push_frame(self):
        new_frame = dbnstate.DBNFrame(
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
        
        ops = 0
        self.terminated = False
        while not self.terminated:
            self.step(trace=trace)

    def step(self, trace=False):
        op, arg = self.bytecode[self.pointer]
        if trace:
            print self.pointer, '%s %s' % (op, arg)

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

    @increments_pc
    def _op_SET_LINE_NO(self, arg):
        line_no = int(arg)
        if line_no == -1:
            raise RuntimeError("Why is line_no being set to -1??")
        else:
            self.line_no = line_no

    @increments_pc
    def _op_STORE(self, arg):
        val = self.stack.pop()
        self.frame.bind_variable(arg, val)

    @increments_pc
    def _op_LOAD(self, arg):
        val = self.frame.lookup_variable(arg, default=DEFAULT_VARIABLE_VALUE)
        self.stack.append(val)

    @increments_pc
    def _op_LOAD_INTEGER(self, arg):
        self.stack.append(int(arg))

    @increments_pc
    def _op_LOAD_STRING(self, arg):
        self.stack.append(arg)

    @increments_pc
    @pops_top(3)
    def _op_SET_DOT(self, x, y, val):
        self.image.set_pixel(x, y, val)

    @increments_pc
    @pops_top(2)
    def _op_GET_DOT(self, x, y):
        val = self.image.query_pixel(x, y)
        self.stack.append(val)

    @increments_pc
    @pops_top(2)
    def _op_BINARY_ADD(self, top, top1):
        self.stack.append(top + top1)

    @increments_pc
    @pops_top(2)
    def _op_BINARY_SUB(self, top, top1):
        self.stack.append(top - top1)

    @increments_pc
    @pops_top(2)
    def _op_BINARY_DIV(self, top, top1):
        self.stack.append(top / top1)

    @increments_pc
    @pops_top(2)
    def _op_BINARY_MUL(self, top, top1):
        self.stack.append(top * top1)

    @increments_pc
    @pops_top(2)
    def _op_COMPARE_SAME(self, top, top1):
        self.stack.append(int(top == top1))

    @increments_pc
    @pops_top(2)
    def _op_COMPARE_NSAME(self, top, top1):
        self.stack.append(int(top != top1))

    @increments_pc
    @pops_top(2)
    def _op_COMPARE_SMALLER(self, top, top1):
        self.stack.append(int(top < top1))

    @increments_pc
    @pops_top(2)
    def _op_COMPARE_NSMALLER(self, top, top1):
        self.stack.append(int(top >= top1))

    @increments_pc
    def _op_DUP_TOPX(self, arg):
        c = int(arg)
        dups = self.stack[-c:]
        self.stack.extend(dups)

    @increments_pc
    def _op_POP_TOPX(self, arg):
        c = int(arg)
        for i in range(c):
            self.stack.pop()

    @increments_pc
    @pops_top(2)
    def _op_ROT_TWO(self, top, top1):
        self.stack.append(top)
        self.stack.append(top1)

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

    @increments_pc
    def _op_DEFINE_COMMAND(self, arg):
        command_pointer = self.stack.pop()
        command_name = self.stack.pop()

        argc = int(arg)
        formal_args = [self.stack.pop() for i in range(argc)]
        command = structures.DBNCommand(formal_args, command_pointer)
        self.commands[command_name] = command

    def _op_COMMAND(self, arg):
        command_name = self.stack.pop()

        command = self.commands.get(command_name)
        if command is None:
            raise RuntimeError('No such command! %s' % command_name)

        argc = int(arg)
        if not argc == command.argc:
            raise RuntimeError('bad argc')

        evaled_args = [self.stack.pop() for i in range(argc)]
        
        if command.is_builtin:
            command.call(self, *evaled_args)
            self.stack.append(0)
            self.pointer += 1

        else:
            # push a frame
            self.push_frame()
            
            # bind the variables
            self.frame.bind_variables(**dict(zip(command.formal_args, evaled_args)))
            
            # jump!
            self.pointer = command.body_pointer
    
    @pops_top(1)
    def _op_RETURN(self, retval):
        # return val is TOP
        # TODO error guard / catch

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

        self.debug(self.dump_bytecode())

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
    