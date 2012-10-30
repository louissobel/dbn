"""
This module has the classes
for all the nodes in the AST
of a dbn program


note on line number tracking:
done using a line_no attribute
Commands and Keywords (Set, Repeat, Questions... (block level nodes))
are the ones that this matters for

Also, note that the line_no of the stored procedure created by the
DefineCommandNode gets set to the line_no of the DefineCommandNode
"""
from structures import DBNDot, DBNVariable, DBNProcedure

VERBOSE = False

class DBNBaseNode:
    
    def __init__(self, tokens=None):
        self.line_no = -1
        
        if tokens is None:
            self.tokens = []
        else:
            self.tokens = tokens
    
    def start_location(self):
        """
        returns a "lineno.charno" of where it starts
        or None if it has no tokens
        """
        if self.tokens:
            first_token = self.tokens[0]
            return "%d.%d" % (first_token.line_no, first_token.char_no - 1)
        else:
            return None
            
    def end_location(self):
        """
        retusn a "lineno.charno" of where it ends
        or None if it has no tokens
        """
        if self.tokens:
            last_token = self.tokens[-1]
            return "%d.%d" % (last_token.line_no, last_token.end_char_no - 1)
        else:
            return None
        
        

class DBNBlockNode(DBNBaseNode):

    display_name = 'block'

    def __init__(self, *args, **kwargs):
        tokens = kwargs.get('tokens')
        DBNBaseNode.__init__(self, tokens=tokens)
        self.children = args

    def apply(self, state):
        """
        applys this node against the given state

        returns the state
        """
        for child in self.children:
            state = child.apply(state)
        return state

    def __str__(self):
        return "(eval %s)" % ' '.join([str(c) for c in self.children])

    def pprint(self, depth=0, indent=4):
        print "%s(" % (' ' * depth * indent)
        for child in self.children:
            child.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNSetNode(DBNBaseNode):
    """
    takes care of the special handling for Set
    """

    display_name = 'set'

    def __init__(self, left, right, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.left = left
        self.right = right

    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        left = self.left.evaluate_lazy(state)
        right = self.right.evaluate(state)
        state = state.set(left, right)
        return state

    def __str__(self):
        return "(Set %s %s)" % (self.left, self.right)

    def pprint(self, depth=0, indent=4):
        print "%s(Set" % ((' ' * depth * indent),)
        self.left.pprint(depth=depth + 1, indent=indent)
        self.right.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNRepeatNode(DBNBaseNode):

    display_name = 'repeat'

    def __init__(self, var, start, end, body, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.var = var
        self.start = start
        self.end = end
        self.body = body  # a DBNBlockNode

    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        variable = self.var.evaluate_lazy(state)
        start_val = self.start.evaluate(state)
        end_val = self.end.evaluate(state)

        #+1 because it is end inclusive
        if end_val > start_val:
            repeat_range = range(start_val, end_val + 1)
        else:
            repeat_range = reversed(range(end_val, start_val + 1))

        for variable_value in repeat_range:
            state = state.set_variable(variable.name, variable_value)
            state = self.body.apply(state)

        return state

    def __str__(self):
        return "(Repeat %s %s %s %s)" % (self.var, self.start, self.end, self.body)

    def pprint(self, depth=0, indent=4):
        print "%s(Repeat" % ((' ' * depth * indent),)
        self.var.pprint(depth=depth + 1, indent=indent)
        self.start.pprint(depth=depth + 1, indent=indent)
        self.end.pprint(depth=depth + 1, indent=indent)
        self.body.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
class DBNQuestionNode(DBNBaseNode):
    
    display_name = 'question'
    
    def __init__(self, question_name, lvalue, rvalue, body, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.question_name = question_name
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.body = body
        
    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        left = self.lvalue.evaluate(state)
        right = self.rvalue.evaluate(state)
        
        questions = {
            'Same': lambda l,r: l == r,
            'NotSame': lambda l,r: l != r,
            'Smaller': lambda l,r: l < r,
            'NotSmaller': lambda l,r: l >= r,
        }
        
        do_branch = questions[self.question_name](left, right)
        if do_branch:
            state = self.body.apply(state)
        
        return state
        
    def __str__(self):
        return "(%s %s %s %s)" % (self.question_name, self.lvalue, self.rvalue, self.body)
        
    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.question_name)
        self.lvalue.pprint(depth=depth + 1, indent=indent)
        self.rvalue.pprint(depth=depth + 1, indent=indent)
        self.body.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNCommandNode(DBNBaseNode):

    display_name = 'command'

    def __init__(self, command_name, *args, **kwargs):
        tokens = kwargs.get('tokens')
        DBNBaseNode.__init__(self, tokens=tokens)
        self.command_name = command_name
        self.args = args

    def add_arg(self, node):
        self.args.append(node)

    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        evaluated_args = [arg.evaluate(state) for arg in self.args]
        proc = state.lookup_command(self.command_name)
        if proc is None:
            raise ValueError("Command %s not found!" % self.command_name)

        # get the arg count of proc.. it has to be equal to length of evaluated args
        if proc.arg_count != len(evaluated_args):
            raise ValueError("%s requires %d arguments, but %d given" % \
                (self.command_name, proc.arg_count, len(evaluated_args)))
        
        state = state.push()
        state = state.set_variables(**dict(zip(proc.formal_args, evaluated_args)))
        state = proc.body.apply(state)
        state = state.pop()
        return state

    def __str__(self):
        return "(%s %s)" % (
            self.command_name,
            ' '.join([str(a) for a in self.args])
        )

    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.command_name)
        for arg in self.args:
            arg.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNCommandDefinitionNode(DBNBaseNode):
    
    display_name = 'command_definition'
    
    def __init__(self, name, args, command_body, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.name = name
        self.args = args
        self.command_body = command_body
        
    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        proc = DBNProcedure(self.args, self.command_body)   
        proc.line_no = self.line_no     
        state = state.add_command(self.name, proc)
        return state
        
    def __str__(self):
        return "(define %s (%s) %s)" % (self.name, ','.join(self.args), self.command_body)
        
    def pprint(self, depth=0, indent=4):
        print "%s(define" % ((' ' * depth * indent),)
        print "%s(%s)" % ((' ' * (depth+1) * indent), self.name)
        print "%s(%s)" % ((' ' * (depth+1) * indent), ','.join(self.args))
        self.command_body.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
  
class DBNPythonNode(DBNBaseNode):
    """
    also, never created by the parser, only by me
    """
    
    display_name = 'python'
    
    def __init__(self, function):
        DBNBaseNode.__init__(self, tokens=[])
        self.function = function
        
    def apply(self, state):
        state = self.function(state)
        return state
    
    def __str__(self):
        return "([Native Code])"  # heh
        
    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))
        
    
################################################################
###  These nodes are fundamentally different in that they
###  are stateless expressions. They do not mutate and they
###  expose evaluate or evaluate lazy interface, rather than apply
###
###


class DBNBracketNode(DBNBaseNode):

    display_name = 'dot'

    def __init__(self, left, right, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.left = left
        self.right = right

    def __str__(self):
        return "(bracket %s %s)" % (str(self.left), str(self.right))

    def evaluate(self, state):
        """
        cannot mutate state!
        """
        x = self.left.evaluate(state)
        y = self.right.evaluate(state)
        return state.image.query_pixel(x, y)

    def evaluate_lazy(self, state):
        x = self.left.evaluate(state)
        y = self.right.evaluate(state)
        return DBNDot(x, y)

    def pprint(self, depth=0, indent=4):
        print "%s(bracket" % (' ' * depth * indent)
        self.left.pprint(depth=depth + 1, indent=indent)
        self.right.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNBinaryOpNode(DBNBaseNode):

    display_name = 'operation'

    def __init__(self, operation, left, right, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.operation = operation
        self.left = left
        self.right = right

    def __str__(self):
        return "(%s %s %s)" % (self.operation, str(self.left), str(self.right))

    def evaluate(self, state):
        left = self.left.evaluate(state)
        right = self.right.evaluate(state)

        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '/': lambda a, b: a / b,  # all numbers are always ints!
            '*': lambda a, b: a * b,
        }

        return ops[self.operation](left, right)

    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.operation)
        self.left.pprint(depth=depth + 1, indent=indent)
        self.right.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNNumberNode(DBNBaseNode):

    display_name = 'number'

    def __init__(self, numberstring, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.numberstring = numberstring

    def __str__(self):
        return "(%s)" % self.numberstring

    def evaluate(self, state):
        return int(self.numberstring)

    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))


class DBNWordNode(DBNBaseNode):

    display_name = 'word'

    def __init__(self, wordstring, tokens=None):
        DBNBaseNode.__init__(self, tokens=tokens)
        self.wordstring = wordstring

    def __str__(self):
        return "(%s)" % self.wordstring

    def evaluate(self, state):
        return state.lookup_variable(self.wordstring)

    def evaluate_lazy(self, state=None):
        """
        state is optional here, because we don't need it!
        """
        return DBNVariable(self.wordstring)

    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))
