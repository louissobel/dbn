import sys

import dbnstate

class Interpreter:
    
    def __init__(self, code):
        self.bytecode = code
        self.env = dbnstate.DBNEnvironment()
        self.commands = {}
        self.stack = []
        
        # base pointer
        self.bp = 0
        
        # return pointer
        self.rp = -1
        
        # program count
        self.pointer = 0
    
    def run(self):
        while self.pointer < len(self.bytecode):
            print self.pointer, self.stack, self.env, self.commands

            op, arg = bytecode[self.pointer]
            print '%s %s' % (op, arg)
    
            if op == 'STORE':
                val = self.stack.pop()
                self.env = self.env.set(arg, val)
                self.pointer += 1
    
            elif op == 'LOAD':
                self.stack.append(self.env.get(arg))
                self.pointer += 1
    
            elif op == 'LOAD_INTEGER':
                self.stack.append(int(arg))
                self.pointer += 1
    
            elif op == 'LOAD_STRING':
                self.stack.append(arg)
                self.pointer += 1

            elif op == 'SET_DOT':
                self.pointer += 1
    
            elif op == 'GET_DOT':
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
                self.commands[command_name] = {'p': command_pointer, 'a': formal_args}
                self.pointer += 1
        
            elif op == 'COMMAND':
                command_name = self.stack.pop()

                command = self.commands.get(command_name)
                if command is None:
                    raise ValueError('No such command! %s' % command_name)

                argc = int(arg)
                if not argc == len(command['a']):
                    raise ValueError('bad argc')

                evaled_args = [self.stack.pop() for i in range(argc)]

                self.env = self.env.push()

                # bind the variables
                self.env = self.env.update(dict(zip(command['a'], evaled_args)))

                # stash our base_pointer, return pointer
                self.stack.append(self.bp)
                self.stack.append(self.rp)

                # set our new bp, rp
                self.bp = len(self.stack)
                self.rp = self.pointer + 1

                # lets fucking jump!
                self.pointer = command['p']
            
            elif op == 'RETURN':
                # return val is TOP
                retval = self.stack.pop()
                
                # lets get back to the base
                while len(self.stack) > self.bp:
                    self.stack.pop()

                # save current rp
                return_location = self.rp
                
                # restore old rp, bp
                self.rp = self.stack.pop()
                self.bp = self.stack.pop()
                
                # lets clear the env
                self.env = self.env.pop()
                
                # and put our retval in
                self.stack.append(retval)
                
                # and jump!
                self.pointer = return_location

        print self.pointer, self.stack, self.env, self.commands
        print 'END'
        

if __name__ == "__main__":
    bytecode = []

    for line in sys.stdin:
        n, o, a = line.strip().split()
        bytecode.append((o, a))
    
    i = Interpreter(bytecode)
    i.run()
    