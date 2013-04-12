import sys

import dbnstate
import structures
import adapter_bus

DEFAULT_VARIABLE_VALUE = 0
DEFAULT_INITIAL_PAPER_COLOR = 0
DEFAULT_INITIAL_PEN_COLOR = 100


import time

class DBNInterpreter:

    def __init__(self, code):
        self.bytecode = code

        self.commands = {}
        self.numbers = {}
        
        # the adpater bus to the external world
        self.adapter_bus = adapter_bus.AdapterBus()
        self.adapter_bus.connect(self)
        
        self.image = dbnstate.DBNImage(DEFAULT_INITIAL_PAPER_COLOR)
        self.pen_color = DEFAULT_INITIAL_PEN_COLOR

        # initialize base frame
        base_frame = dbnstate.DBNFrame()
        self.set_frame(base_frame)

        # line no
        self.line_no = -1

        # program count
        self.pointer = 0

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

    def run(self, **kwargs):
        trace = kwargs.get('trace', False)
        
        ops = 0
        while self.pointer < len(self.bytecode):

            op, arg = self.bytecode[self.pointer]
            if trace:
                print self.pointer, '%s %s' % (op, arg)

            if   op == 'SET_LINE_NO':
                line_no = int(arg)
                if line_no == -1:
                    raise RuntimeError("Why is line_no being set to -1??")
                else:
                    self.line_no = line_no
                self.pointer += 1
    
            elif op == 'STORE':
                val = self.stack.pop()
                self.frame.bind_variable(arg, val)
                self.pointer += 1
    
            elif op == 'LOAD':
                val = self.frame.lookup_variable(arg, default=DEFAULT_VARIABLE_VALUE)
                self.stack.append(val)
                self.pointer += 1
    
            elif op == 'LOAD_INTEGER':
                self.stack.append(int(arg))
                self.pointer += 1
    
            elif op == 'LOAD_STRING':
                self.stack.append(arg)
                self.pointer += 1

            elif op == 'SET_DOT':
                x = self.stack.pop()
                y = self.stack.pop()
                val = self.stack.pop()
                self.image.set_pixel(x, y, val)
                self.pointer += 1
    
            elif op == 'GET_DOT':
                x = self.stack.pop()
                y = self.stack.pop()
                val = self.image.query_pixel(x, y)
                self.stack.append(val)
                self.pointer += 1
        
            elif op == 'BINARY_ADD':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(top + top1)
                self.pointer += 1
    
            elif op == 'BINARY_SUB':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(top - top1)
                self.pointer += 1
    
            elif op == 'BINARY_DIV':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(top / top1)
                self.pointer += 1
    
            elif op == 'BINARY_MUL':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(top * top1)
                self.pointer += 1
    
            elif op == 'COMPARE_SAME':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(int(top == top1))
                self.pointer += 1
        
            elif op == 'COMPARE_NSAME':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(int(top != top1))
                self.pointer += 1
    
            elif op == 'COMPARE_SMALLER':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(int(top < top1))
                self.pointer += 1
    
            elif op == 'COMPARE_NSMALLER':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(int(top >= top1))
                self.pointer += 1
    
            elif op == 'DUP_TOPX':
                c = int(arg)
                dups = self.stack[-c:]
                self.stack.extend(dups)
                self.pointer += 1
    
            elif op == 'POP_TOPX':
                c = int(arg)
                for i in range(c):
                    self.stack.pop()
                self.pointer += 1
    
            elif op == 'ROT_TWO':
                top = self.stack.pop()
                top1 = self.stack.pop()
                self.stack.append(top)
                self.stack.append(top1)
                self.pointer += 1
    
            elif op == 'JUMP':
                target = int(arg)
                self.pointer = target
    
            elif op == 'POP_JUMP_IF_FALSE':
                target = int(arg)
                top = self.stack.pop()
                if not top:
                    self.pointer = target
                else:
                    self.pointer += 1
    
            elif op == 'POP_JUMP_IF_TRUE':
                target = int(arg)
                top = self.stack.pop()
                if top:
                    self.pointer = target
                else:
                    self.pointer += 1

            elif op == 'DEFINE_COMMAND':
                command_pointer = self.stack.pop()
                command_name = self.stack.pop()

                argc = int(arg)
                formal_args = [self.stack.pop() for i in range(argc)]
                command = structures.DBNCommand(formal_args, command_pointer)
                self.commands[command_name] = command
                self.pointer += 1
        
            elif op == 'COMMAND':
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
            
            elif op == 'RETURN':
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

            ops += 1
        

if __name__ == "__main__":
    bytecode = []

    for line in sys.stdin:
        n, o, a = line.strip().split()
        bytecode.append((o, a))
    
    i = DBNInterpreter(bytecode)
    i.run()
    