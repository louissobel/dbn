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
    
    type = 'base'
    
    def __init__(self, name=None, children=None, tokens=None, line_no=-1):
        self.line_no = line_no
        self.tokens = tokens or []
        self.children = children or []
        self.name = name or self.type
    
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


    def pformat(self, depth=0, indent=None):
    
        if indent is None:
            return "(%s %s)" % (self.name, [c.pformat(depth, indent) for c in self.children])
        
        else:
            out = " " * indent * depth
            out += "(%s\n" % self.name
            for child in self.children:
                out += child.pformat(depth+1, indent)
            out += " " * indent * depth
            out += ")\n"
            return out
            
    def pprint(self, indent=2):
        print self.pformat(depth=0, indent=indent)
    
    def to_js(self, depth=0):
        """
        we use a four space indent, by the way
        """
        header_lines = [
            "(new DBNASTNode({",
            "  type: '%s'," % self.type,
            "  name: '%s'," % self.name,
            "  tokens: [],",
            "  line_no: %d," % self.line_no,
            "  children: [\n",
        ]

        out = '\n'.join([depth  * "    " + l for l in header_lines])
        for child in self.children:
            out += child.to_js(depth+1) + ',\n'
        
        footer_lines = [
            "  ]",
            "}))",
        ]
        
        out += '\n'.join([depth  * "    " + l for l in footer_lines])
        return out
        

class DBNBlockNode(DBNBaseNode):

    type = 'block'

    def apply(self, state):
        """
        applys this node against the given state

        returns the state
        """
        for child in self.children:
            state = child.apply(state)
        return state


class DBNSetNode(DBNBaseNode):
    """
    takes care of the special handling for Set
    """

    type = 'set'

    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        left, right = children
        
        left = left.evaluate_lazy(state)
        right = right.evaluate(state)
        
        state = state.set(left, right)
        return state


class DBNRepeatNode(DBNBaseNode):

    type = 'repeat'

    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        var, start, end, body = self.children
        
        variable = var.evaluate_lazy(state)
        start_val = start.evaluate(state)
        end_val = end.evaluate(state)

        #+1 because it is end inclusive
        if end_val > start_val:
            repeat_range = range(start_val, end_val + 1)
        else:
            repeat_range = reversed(range(end_val, start_val + 1))

        for variable_value in repeat_range:
            state = state.set_variable(variable.name, variable_value)
            state = body.apply(state)

        return state


class DBNQuestionNode(DBNBaseNode):
    
    type = 'question'
        
    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        lvalue, rvalue, body = self.children
        
        left = lvalue.evaluate(state)
        right = rvalue.evaluate(state)
        
        questions = {
            'Same': lambda l,r: l == r,
            'NotSame': lambda l,r: l != r,
            'Smaller': lambda l,r: l < r,
            'NotSmaller': lambda l,r: l >= r,
        }
        
        do_branch = questions[self.name](left, right)
        if do_branch:
            state = body.apply(state)
        
        return state


class DBNCommandNode(DBNBaseNode):

    type = 'command'

    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        evaluated_args = [arg.evaluate(state) for arg in self.children]
        proc = state.lookup_command(self.name)
        if proc is None:
            raise ValueError("Command %s not found!" % self.name)

        # get the arg count of proc.. it has to be equal to length of evaluated args
        if proc.arg_count != len(evaluated_args):
            raise ValueError("%s requires %d arguments, but %d given" % \
                (self.name, proc.arg_count, len(evaluated_args)))
        
        state = state.push()
        state = state.set_variables(**dict(zip(proc.formal_args, evaluated_args)))
        state = proc.body.apply(state)
        state = state.pop()
        return state


class DBNCommandDefinitionNode(DBNBaseNode):
    
    type = 'command_definition'
       
    def apply(self, state):
        state = state.set_line_no(self.line_no)
        
        # [name, arg1, ..., argN, body]
        command_name = self.children[0].evaluate_lazy().name
        args = [word.evaluate_lazy().name for word in self.children[1:-1]]
        body = self.children[-1]

        proc = DBNProcedure(args, body, line_no=self.line_no)

        state = state.add_command(command_name, proc)
        return state

  
class DBNPythonNode(DBNBaseNode):
    """
    also, never created by the parser, only by me
    """
    type = 'python'
    
    def __init__(self, function):
        DBNBaseNode.__init__(self, tokens=[])
        self.function = function
        
    def apply(self, state):
        state = self.function(state)
        return state
        
    
################################################################
###  These nodes are fundamentally different in that they
###  are stateless expressions. They do not mutate and they
###  expose evaluate or evaluate lazy interface, rather than apply
###
###


class DBNBracketNode(DBNBaseNode):

    type = 'bracket'

    def evaluate(self, state):
        """
        cannot mutate state!
        """
        left, right = self.children
        
        x = left.evaluate(state)
        y = right.evaluate(state)
        return state.image.query_pixel(x, y)

    def evaluate_lazy(self, state):
        left, right = self.children
        
        x = left.evaluate(state)
        y = right.evaluate(state)
        return DBNDot(x, y)


class DBNBinaryOpNode(DBNBaseNode):

    type = 'operation'

    def __str__(self):
        return "(%s %s %s)" % (self.operation, str(self.left), str(self.right))

    def evaluate(self, state):
        left, right = self.children
        
        left = left.evaluate(state)
        right = right.evaluate(state)

        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '/': lambda a, b: a / b,  # all numbers are always ints!
            '*': lambda a, b: a * b,
        }

        return ops[self.name](left, right)


class DBNNumberNode(DBNBaseNode):

    type = 'number'

    def evaluate(self, state):
        return int(self.name)

    def pformat(self, depth, indent):
        return "%s(number %s)\n" % (" "*depth*indent, self.name)

class DBNWordNode(DBNBaseNode):

    type = 'word'


    def evaluate(self, state):
        return state.lookup_variable(self.name)

    def evaluate_lazy(self, state=None):
        """
        state is optional here, because we don't need it!
        """
        return DBNVariable(self.name)
        
    def pformat(self, depth, indent):
        return "%s(word %s)\n" % (" "*depth*indent, self.name)

