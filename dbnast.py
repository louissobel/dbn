"""
This module has the classes
for all the nodes in the AST
of a dbn program
"""
import utils


class DBNBaseNode:
    pass


class DBNBlockNode(DBNBaseNode):

    display_name = 'block'

    def __init__(self, *args):
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


class DBNCommandNode(DBNBaseNode):

    display_name = 'command'

    def __init__(self, command_name, *args):
        self.command_name = command_name
        self.args = args

    def add_arg(self, node):
        self.args.append(node)

    def apply(self, state):
        # args cannot mutate
        evaluated_args = [arg.evaluate(state) for arg in self.args]
        state = state.run_command(self.command_name, evaluated_args)
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


class DBNSetNode(DBNBaseNode):
    """
    takes care of the special handling for Set
    """

    display_name = 'set'

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def apply(self, state):
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

    def __init__(self, var, start, end, body):
        self.var = var
        self.start = start
        self.end = end
        self.body = body  # a DBNBlockNode

    def apply(self, state):
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
    
    def __init__(self, question_name, lvalue, rvalue, body):
        self.question_name = question_name
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.body = body
        
    def apply(self, state):
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
    
    
################################################################
###  These nodes are fundamentally different in that they
###  are stateless expressions. They do not mutate and they
###  expose evaluate or evaluate lazy interface, rather than apply
###
###


class DBNBracketNode(DBNBaseNode):

    display_name = 'dot'

    def __init__(self, left, right):
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
        return utils.DBNDot(x, y)

    def pprint(self, depth=0, indent=4):
        print "%s(bracket" % (' ' * depth * indent)
        self.left.pprint(depth=depth + 1, indent=indent)
        self.right.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)


class DBNBinaryOpNode(DBNBaseNode):

    display_name = 'operation'

    def __init__(self, operation, left, right):
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

    def __init__(self, numberstring):
        self.numberstring = numberstring

    def __str__(self):
        return "(%s)" % self.numberstring

    def evaluate(self, state):
        return int(self.numberstring)

    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))


class DBNWordNode(DBNBaseNode):

    display_name = 'word'

    def __init__(self, wordstring):
        self.wordstring = wordstring

    def __str__(self):
        return "(%s)" % self.wordstring

    def evaluate(self, state):
        return state.lookup_variable(self.wordstring)

    def evaluate_lazy(self, state=None):
        """
        state is optional here, because we don't need it!
        """
        return utils.DBNVariable(self.wordstring)

    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))