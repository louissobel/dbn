
from dbnast import *

class DBNCompiler:
    
    def __init__(self):
        self.bytecodes = []
        self.commands = {}
        self.counter = 0
    
    def add(self, code, arg=None):
        self.bytecodes.append((code, arg))
        self.counter += 1
        return self
    
    def extend(self, other):
        for bc in other.bytecodes:
            self.add(*bc)

    def compile(self, node):
        new = DBNCompiler()
        if   isinstance(node, DBNBlockNode):
            new.compile_block(node)

        elif isinstance(node, DBNSetNode):
            new.compile_set(node)
        
        elif isinstance(node, DBNRepeatNode):
            new.compile_repeat(node)
        
        elif isinstance(node, DBNQuestionNode):
            new.compile_question(node)
        
        elif isinstance(node, DBNCommandNode):
            new.compile_command(node)
        
        elif isinstance(node, DBNCommandDefinitionNode):
            new.compile_command_definition(node)
        
        elif isinstance(node, DBNBracketNode):
            new.compile_bracket(node)
        
        elif isinstance(node, DBNBinaryOpNode):
            new.compile_binary_op(node)
        
        elif isinstance(node, DBNNumberNode):
            new.compile_number(node)
        
        elif isinstance(node, DBNWordNode):
            new.compile_word(node)
        
        else:
            raise ValueError("Unknown node type!")
        
        return new
        
    def compile_block(self, node):
        for subnode in node.children:
            self.extend(self.compile(subnode))

    def compile_set(self, node):
        left, right = node.children

        self.extend(self.compile(right))

        # If left is a bracket, its a store_bracket op
        if   isinstance(left, DBNBracketNode):
            # Peer inside the bracket
            bracket_left, bracket_right = left.children
            
            self.extend(self.compile(bracket_right))
            self.extend(self.compile(bracket_left))

            self.add('SET_DOT')

        elif isinstance(left, DBNWordNode):
            self.add('STORE', left.name)

    def compile_repeat(self, node):
        var, start, end, body = node.children
        
        # push on end
        self.extend(self.compile(end))
        # push on start
        self.extend(self.compile(start))

        # body entry - [end, current]
        body_entry = self.counter

        # dup current for store
        self.add('DUP_TOPX', 1)
        self.add('STORE', var.name)

        self.extend(self.compile(body))

        # dup [end, current] for comparison
        self.add('DUP_TOPX', 2)

        # compare
        self.add('COMPARE_SAME')
        # now stack is [end, current, current<end]
        # if current is not less than end, lets GTFO
        skip_count = 8
        self.add('POP_JUMP_IF_TRUE', self.counter + skip_count + 1)

        # if we are here, we need either to increment or decrement
        self.add('DUP_TOPX', 2)
        self.add('COMPARE_SMALLER')
        self.add('POP_JUMP_IF_FALSE', self.counter + 3) # the else
        
        self.add('LOAD_INTEGER', 1)
        self.add('JUMP', self.counter + 2)
        
        self.add('LOAD_INTEGER', -1)

        # ok if we are here, we are good to increment (decrement) and repeat
        # (these are the ones counted in skip_count)
        self.add('BINARY_ADD')
        self.add('JUMP', body_entry)

        # ok, now this stuff is cleanup - pop away
        self.add('POP_TOPX', 2)

    def compile_question(self, node):
        left, right, body = node.children
        
        self.extend(self.compile(right))
        self.extend(self.compile(left))

        questions = {
            'Same': 'COMPARE_SAME',
            'NotSame': 'COMPARE_NSAME',
            'Smaller': 'COMPARE_SMALLER',
            'NotSmaller': 'COMPARE_NSMALLER'
        }

        self.add(questions[node.name])
        
        body = self.compile(body)
        after_body = self.counter + body.counter + 1

        self.add('POP_JUMP_IF_FALSE', after_body)
        self.extend(body)

    def compile_command(self, node):
        raise NotImplemented

    def compile_command_definition(self, node):
        # children:
        # [name, arg1, ..., argN, body]
        

            # [name, arg1, ..., argN, body]
            command_name = self.children[0].evaluate_lazy().name
            args = [word.evaluate_lazy().name for word in self.children[1:-1]]
            body = self.children[-1]

            proc = DBNProcedure(args, body, line_no=self.line_no)

            state = state.add_command(command_name, proc)
            return state


    def compile_bracket(self, node):
        # this compiles it as read
        # will be compiled as write by compile_set
        left, right = node.children

        self.extend(self.compile(right))
        self.extend(self.compile(left))

        self.add('GET_DOT')

    def compile_binary_op(self, node):
        left, right = node.children

        self.compile(right)
        self.compile(left)

        ops = {
            '+': 'BINARY_ADD',
            '-': 'BINARY_SUB',
            '/': 'BINARY_DIV',
            '*': 'BINARY_MUL',
        }
        self.add(ops[node.name])

    def compile_number(self, node):
        self.add('LOAD_INTEGER', node.name)

    def compile_word(self, node):
        self.add('LOAD', node.name)



    