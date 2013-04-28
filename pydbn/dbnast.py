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

class DBNBaseNode(object):
    """
    base node
    """
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

class DBNProgramNode(DBNBaseNode):
    """
    a whole DBNProgram
    """
    type = 'program'


class DBNBlockNode(DBNBaseNode):
    """
    A block of DBN code
    """
    type = 'block'


class DBNSetNode(DBNBaseNode):
    """
    takes care of the special handling for Set
    """
    type = 'set'
    
    @property
    def left(self):
        return self.children[0]
    
    @property
    def right(self):
        return self.children[1]


class DBNRepeatNode(DBNBaseNode):
    """
    A repeat
    """
    type = 'repeat'
    
    @property
    def var(self):
        return self.children[0]
    
    @property
    def start(self):
        return self.children[1]
    
    @property
    def end(self):
        return self.children[2]
    
    @property
    def body(self):
        return self.children[3]


class DBNQuestionNode(DBNBaseNode):
    """
    Represents a question
    """
    type = 'question'
    
    @property
    def left(self):
        return self.children[0]
    
    @property
    def right(self):
        return self.children[1]
    
    @property
    def body(self):
        return self.children[2]


class DBNCommandNode(DBNBaseNode):
    """
    A command invocation
    """
    type = 'command'

    @property
    def args(self):
        return self.children


class DBNCommandDefinitionNode(DBNBaseNode):
    """
    The definition of a command
    """
    type = 'command_definition'

    @property
    def command_name(self):
        return self.children[0]
    
    @property
    def args(self):
        return self.children[1:-1]
    
    @property
    def body(self):
        return self.children[-1]


class DBNBracketNode(DBNBaseNode):
    """
    Represents a bracket notation pixel reference
    """
    type = 'bracket'
    
    @property
    def left(self):
        return self.children[0]
    
    @property
    def right(self):
        return self.children[1]


class DBNBinaryOpNode(DBNBaseNode):
    """
    arbitrary binary operation
    """
    type = 'binary_op'
    
    @property
    def left(self):
        return self.children[0]
    
    @property
    def right(self):
        return self.children[1]


class DBNLoadNode(DBNBaseNode):
    """
    A load statement
    """
    type = 'load'

    def pformat(self, depth, indent):
        return "%s(load %s)\n" % (" "*depth*indent, self.name)


class DBNNumberNode(DBNBaseNode):
    """
    A number literal
    """
    type = 'number'
    
    def pformat(self, depth, indent):
        return "%s(number %s)\n" % (" "*depth*indent, self.name)


class DBNWordNode(DBNBaseNode):
    """
    a variable literal
    """
    type = 'word'
    
    def pformat(self, depth, indent):
        return "%s(word %s)\n" % (" "*depth*indent, self.name)


class DBNNoopNode(DBNBaseNode):
    """
    a noop
    """
    type = 'noop'
    
    def pformat(self, depth, indent):
        return "%s(noop)" % (" "*depth*indent, )

