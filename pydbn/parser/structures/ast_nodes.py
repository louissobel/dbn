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


class DBNBaseNode(object):
    """
    base node
    """

    type = 'base'
    
    def __init__(self, value=None, children=None, tokens=None, line_no=-1):
        self.line_no = line_no
        self.value = value
        self.tokens = tokens or []
        self.children = children or []

    def pformat_terminal(self, depth=0, indent=None):
        if indent is None:
            return "(%s %s)" % (self.type, self.value)
        else:
            return "%s(%s %s)" % (" "*depth*indent, self.type, self.value)

    def pformat(self, depth=0, indent=None):
        
        if indent is None:
            return "(%s %s)" % (self.type, ' '.join([c.pformat(depth, indent) for c in self.children]))
        
        else:
            out = " " * indent * depth
            out += "(%s\n" % self.type
            for child in self.children:
                out += child.pformat(depth+1, indent)
            out += " " * indent * depth
            out += ")\n"
            return out
    
    def pprint(self, indent=2):
        print self.pformat(depth=0, indent=indent)

    def __str__(self):
        return self.pformat()


AST_NODE_CLASSES = []
def node(cls):
    """
    class decorator for nodes
    Currently just registers their name
    """
    AST_NODE_CLASSES.append(cls)
    return cls

def terminal_node(cls):
    """
    class decorator for terminals
    Currently just sets pformat to new pformat
    """

    # The replaced pformat
    def pformat(self, *args, **kwargs):
        return self.pformat_terminal(*args, **kwargs)

    cls.pformat = pformat

    return cls

@node
class DBNProgramNode(DBNBaseNode):
    """
    a whole DBNProgram
    """
    type = 'program'


@node
class DBNBlockNode(DBNBaseNode):
    """
    A block of DBN code
    """
    type = 'block'


@node
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


@node
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


@node
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


@node
class DBNCommandNode(DBNBaseNode):
    """
    A command invocation
    """
    type = 'command'

    @property
    def args(self):
        return self.children


@node
class DBNProcedureDefinitionNode(DBNBaseNode):
    """
    The definition of a command
    """
    type = 'procedure_definition'

    @property
    def procedure_name(self):
        return self.children[0]
    
    @property
    def args(self):
        return self.children[1:-1]
    
    @property
    def body(self):
        return self.children[-1]

    @property
    def procedure_type(self):
        if self.value == 'COMMAND':
            return 'command'
        elif self.value == 'NUMBERDEF':
            return 'number'
        else:
            raise ValueError('Unknown procedure definition node value: %s' % self.value)


@node
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


@node
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


@node
@terminal_node
class DBNLoadNode(DBNBaseNode):
    """
    A load statement
    """
    type = 'load'


@node
@terminal_node
class DBNNumberNode(DBNBaseNode):
    """
    A number literal
    """
    type = 'number'


@node
@terminal_node
class DBNWordNode(DBNBaseNode):
    """
    a variable literal
    """
    type = 'word'


@node
@terminal_node
class DBNNoopNode(DBNBaseNode):
    """
    a noop
    """
    type = 'noop'
