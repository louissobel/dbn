"""
whoo ast trees
"""
import utils

class DBNBaseNode:
    pass
     
class DBNBlockNode(DBNBaseNode):
    
    def __init__(self):
        self.children = []
        
    def add_child(self, node):
        self.children.append(node)
        
        
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
            child.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
class DBNCommandNode(DBNBaseNode):
    
    def __init__(self, command_name, args):
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
        return "(%s %s)" % (self.command_name, ' '.join([str(a) for a in self.args]))
        
    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.command_name)
        for arg in self.args:
            arg.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
class DBNSetNode(DBNBaseNode):
    """
    takes care of the special handling for Set
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def apply(self, state):
        left = self.left.evaluate_lazy(state)
        right = self.right.evaluate(state)
        state = state.run_command("Set", [left, right])
        return state

    def __str__(self):
        return "(Set %s)" % (' '.join([str(a) for a in self.args]))

    def pprint(self, depth=0, indent=4):
        print "%s(Set" % ((' ' * depth * indent),)
        self.left.pprint(depth=depth+1, indent=indent)
        self.right.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
class DBNRepeatNode(DBNBaseNode):
    def __init__(self, var, start, end, body):
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        
    def apply(self, state):
        variable = self.var.evaluate_lazy(state)
        
        start_val = self.start.evaluate(state)
        end_val = self.end.evaluate(state)
        
        # body is a DBNBlockNode
        
        if end_val > start_val:
            repeat_range = range(start_val, end_val + 1)
        else:
            repeat_range = reversed(range(end_val, start_val+1))
        
        for variable_value in repeat_range: #+1 because it is end inclusive
            state = state.set_variable(variable.name, variable_value)
            state = self.body.apply(state)
        
        return state
        
    def __str__(self):
        return "(Repeat %s %s %s %s)" % [str(t) for t in (self.var, self.start, self.end, self.body)]
    
    def pprint(self, depth=0, indent=4):
        print "%s(Repeat" % ((' ' * depth * indent),)
        self.var.pprint(depth=depth+1, indent=indent)
        self.start.pprint(depth=depth+1, indent=indent)
        self.end.pprint(depth=depth+1, indent=indent)
        self.body.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
     
################################################################
###  These nodes are fundamentally different in that they
###  are stateless expressions. They do not mutate and they
###  expose evaluate or evaluate lazy interface, rather than apply         
###
###


class DBNBracketNode(DBNBaseNode):
    
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
        self.left.pprint(depth=depth+1, indent=indent)
        self.right.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
            
class DBNBinaryOpNode(DBNBaseNode):
    
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
            '+' : lambda a,b : a + b,
            '-' : lambda a,b : a - b,
            '/' : lambda a,b : a / b, # all numbers are always ints!
            '*' : lambda a,b : a * b,
        }
        
        return ops[self.operation](left, right)
        
        
    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.operation)
        self.left.pprint(depth=depth+1, indent=indent)
        self.right.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
                
class DBNNumberNode(DBNBaseNode):
    
    def __init__(self, numberstring):
        self.numberstring = numberstring
        
    def __str__(self):
        return "(%s)" % self.numberstring
        
    def evaluate(self, state):
        return int(self.numberstring)
    
    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))
               
class DBNWordNode(DBNBaseNode):
    
    def __init__(self, wordstring):
        self.wordstring = wordstring
        
    def __str__(self):
        return "(%s)" % self.wordstring
        
    def evaluate(self, state):
        return state.lookup_variable(self.wordstring)
        
    def evaluate_lazy(self, state):
        return utils.DBNVariable(self.wordstring)
        
    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))