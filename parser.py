"""
a module that implements the parsing classes
"""
from dbnast import *

          
def parse_block(tokens, top_level=False):
    """
    parses a block of statements
    currently handles:
    
    Load, Command only allowed when top_level is True
    
    set
    repeat
    question
    Command (procedure) (if commands_allowed)
    load
    word \implies command
    """    
    block_nodes = []
    while tokens:
        first_token = tokens.pop(0)

        if first_token.type == 'SET':
            set_tokens = collect_until_next(tokens, 'NEWLINE')
            set_node = parse_set(set_tokens)
            block_nodes.append(set_node)
            
        elif first_token.type == 'REPEAT':
            arg_tokens = collect_until_next(tokens, 'OPENBRACE')
            body_tokens = collect_until_balanced(tokens, 'OPENBRACE', 'CLOSEBRACE')
            repeat_node = parse_repeat(arg_tokens, body_tokens)
            block_nodes.append(repeat_node)
            
        elif first_token.type == 'QUESTION':
            arg_tokens = collect_until_next(tokens, 'OPENBRACE')
            body_tokens = collect_until_balanced(tokens, 'OPENBRACE', 'CLOSEBRACE')
            question_name = first_token.value
            question_node = parse_question(question_name, arg_tokens, body_tokens)
            block_nodes.append(question_node)
            
        elif first_token.type == 'COMMAND':
            if top_level:
                arg_tokens = collect_until_next(tokens, 'OPENBRACE')
                body_tokens = collect_until_balanced(tokens, 'OPENBRACE', 'CLOSEBRACE')
                define_command_node = parse_define_command(arg_tokens, body_tokens)
                block_nodes.append(define_command_node)
            else:
                raise ValueError("Command keyowrd only allowed at top level")
            
        elif first_token.type == 'LOAD':
            if top_level:
                load_node = parse_load(first_token)
                block_nodes.append(load_node)
            else:
                raise ValueError("Load keyword only allowed at top level")
        
        elif first_token.type == 'WORD':
            # then we treat it as a command :/
            arg_tokens = collect_until_next(tokens, 'NEWLINE')
            command_name = first_token.value        
            command_node = parse_command(command_name, arg_tokens)
            block_nodes.append(command_node)
            
        elif first_token.type == 'NEWLINE':
            # then it is just an extra blank new line...
            # and we throw it away
            pass
            
        else:
            raise ValueError('I dont know how to parse a %s in a block' % str(first_token))
    
    return DBNBlockNode(*block_nodes)

def parse_command(command_name, arg_tokens):
    """
    parses a command
    """
    args = parse_args(arg_tokens)    
    return DBNCommandNode(command_name, *args) # eeks, digging into the node here
    
def parse_set(arg_tokens):
    """
    parses a Set
    """
    args = parse_args(arg_tokens)
    valid, error = assert_args(args, length=2, match=((DBNBracketNode, DBNWordNode), ) )
    if not valid:
        raise ValueError("Bad arguments parsing Set: %s" % error)
    
    lvalue, rvalue = args
    
    return DBNSetNode(lvalue, rvalue)
            
def parse_repeat(arg_tokens, body_tokens):
    """
    parses a Repeat
    """
    strip_newline(arg_tokens) # newline between args and bracket is optional

    args = parse_args(arg_tokens)
    valid, error = assert_args(args, length=3, match=(DBNWordNode, ))
    if not valid:
        raise ValueError("bad arguments while parsing Repeat: %s" % error)
        
    body = parse_block(body_tokens)
    
    var, start, end = args
    
    return DBNRepeatNode(var, start, end, body)
    
def parse_question(question_name, arg_tokens, body_tokens):
    """
    parses a question!
    """
    strip_newline(arg_tokens)
    
    args = parse_args(arg_tokens)
    valid, error = assert_args(args, length=2)
    if not valid:
        raise ValueError("bad arguments while parsing question %s: " % (question_name, error))
        
    body = parse_block(body_tokens)
    
    lvalue, rvalue = args
    
    return DBNQuestionNode(question_name, lvalue, rvalue, body)

def parse_define_command(arg_tokens, body_tokens):
    """
    parses a command definition!
    """
    # arg tokens MUST ALL BE WORDS. so we can bypass the normal parsing route.
    args = []
    for index, arg_token in enumerate(arg_tokens):
        if not arg_token.type == 'WORD':
            raise ValueError(
                "Every argument to Command must be a WORD. arg %d is a %s" %
                (index, arg_token.type)
            )
        args.append(arg_token.value)
        
    # we must have at least one!
    if not args:
        raise ValueError("There must be at least one argument to Command!")
    
    command_name = args[0]
    formal_args = args[1:]
    
    body = parse_block(body_tokens)
    
    # ah.. ok.. lets not allow any commands within commands.
    return DBNCommandDefinitionNode(command_name, formal_args, body)
    
    
def parse_load(load_token):
    """
    parses a Load statement
    """
    load_path = load_token.value
    return DBNLoadNode(load_path)
    
    
def parse_bracket(tokens):
    """
    ok, so tokens is everything in the brackets

    pretty simple... call parse args on tokens, then make sure that
    there are only two, then store left, right
    """
    args = parse_args(tokens)
    valid, error = assert_args(args, length=2)
    if not valid:
        raise ValueError("Bad bracket contents: %s" % error)
        
    left = args[0]
    right = args[1]

    return DBNBracketNode(left, right) 
    
def parse_args(tokens):
    """
    tokens is a series of tokens that represents some arguments
    4 5 6
    a b c
    a [...] (...)
    
    returns a list of arguments
    """ 
    arg_list = []
    while tokens:
        first_token = tokens.pop(0)
        
        # i know how to handle NUMBER, WORD, OPENPAREN and OPENBRACKET
        if first_token.type == 'NUMBER':
            arg_list.append(parse_number(first_token))
        
        elif first_token.type == 'WORD':
            arg_list.append(parse_word(first_token))
            
        elif first_token.type == 'OPENPAREN':
            arithmetic_tokens = collect_until_balanced(tokens, 'OPENPAREN', 'CLOSEPAREN')
            arg_list.append(parse_arithmetic(arithmetic_tokens))
        
        elif first_token.type == 'OPENBRACKET':
            bracket_tokens = collect_until_balanced(tokens, 'OPENBRACKET', 'CLOSEBRACKET')
            arg_list.append(parse_bracket(bracket_tokens))
            
        else:
            raise ValueError("I don't know how to handle token type %s while parsing args!" % first_token.type)
            
    return arg_list
    
def parse_arithmetic(tokens):
    """
    mega function to parse a set of tokens representing 'arithmatic'
    
    so algorithm:
    we walk down to precedence levels, looking for things.
    if we find one, look for its left,
    and its right, combine them!
    
    would love to make this recrusive to match the rest of how I parse.
    but. I'd also love to be an astronaut
    """
    PRECEDENCE = ['*', '/', '-', '+'] # ok?
    
    # first build a list of nodes, separated by operation tokens
    nodes_and_ops = []
    while tokens:
        first_token = tokens.pop(0)
        if first_token.type == 'WORD':
            nodes_and_ops.append(parse_word(first_token))
        
        elif first_token.type == 'NUMBER':
            nodes_and_ops.append(parse_number(first_token))
        
        elif first_token.type == 'OPENPAREN':
            arithmetic_tokens = collect_until_balanced(tokens, 'OPENPAREN', 'CLOSEPAREN')
            nodes_and_ops.append(parse_arithmetic(arithmetic_tokens))
        
        elif first_token.type == 'OPENBRACKET':
            bracket_tokens = collect_until_balanced(tokens, 'OPENBRACKET', 'CLOSEBRACKET')
            nodes_and_ops.append(parse_bracket(bracket_tokens))
            
        elif first_token.type == 'OPERATOR':
            nodes_and_ops.append(first_token.value)
    
    # now we take multiple passes over that list, reducing
    # it by making binary operations, until it only has one
    # root binary operation node
    while len(nodes_and_ops) > 1:
        #look down the operator precedence chain
        #find a location where that operator occurs
        active_operation = None
        active_index = None  # of the nodes_and_ops list
        for operation in PRECEDENCE:
            active_operation = operation
            found = False
            for index, node_or_op in enumerate(nodes_and_ops):
                if node_or_op == active_operation:
                    found = True
                    active_index = index
            if found:
                break
                
        # so now we now where we have to do our thing
        # active index is the index in node_or_op where
        # the operation that we are going to compress is found
        left_index = active_index - 1
        right_index = active_index + 1
        
        # some structural validation...
        try:
            left_node = nodes_and_ops[left_index]
        except IndexError:
            raise ValueError("There is no node! to the left of the %s operation" % active_operation)
            
        try:
            right_node = nodes_and_ops[right_index]
        except IndexError:
            raise ValueError("There is no node! to the right of the %s operation" % active_operation)
        
        # some semanitc? validation...
        if isinstance(left_node, basestring):
            raise ValueError("The node to the left is not a node, but a string! %s" % left_node)
            
        if isinstance(right_node, basestring):
            raise ValueError("The node to the right is not a node, but a string! %s" % right_node)
            
        # ok but here, we know that they are both nodes (and they both exist!)
        new_node = DBNBinaryOpNode(active_operation, left_node, right_node)
        
        new_nodes_and_ops = []
        for index, node_or_op in enumerate(nodes_and_ops):
            if index == left_index:
                pass
            elif index == right_index:
                pass
            elif index == active_index:
                new_nodes_and_ops.append(new_node)
            else:
                new_nodes_and_ops.append(node_or_op)
                
        nodes_and_ops = new_nodes_and_ops

    return nodes_and_ops[0] # a DBNBinaryOpNode
                            
def parse_word(token):
    """
    token is just one token
    """
    return DBNWordNode(token.value)
    
def parse_number(token):
    """
    token is just one token
    """
    return DBNNumberNode(token.value)


def collect_until_next(tokens, token_type):
    """
    will return a list of tokens unit the next
    one of type token_type or the end of the list
    
    throws away the terminating token of type token_type
    """
    out_tokens = []
    while tokens:
      next_token = tokens.pop(0)
      if next_token.type == token_type:
          break
      else:
          out_tokens.append(next_token)
    return out_tokens

def collect_until_balanced(tokens, left_type, right_type):
    """
    will parse until a balance is found

    assumes that there is already a score of 1 (one open)
    
    throws away the final right_type token
    """
    if left_type == right_type:
      raise AssertionError("louis, why is left_type == right_type?")

    score = 1 # will return once 0
    out_tokens = []
    while tokens:
      next_token = tokens.pop(0)
      if next_token.type == right_type:
          score -= 1
          if score == 0:
              break
      elif next_token.type == left_type:
          score += 1

      out_tokens.append(next_token)
    return out_tokens    

def assert_args(args, length=None, match=None):
    """
    makes sure the given argument list matches the given constraints
    
    length - the number of arguments. if None, can be any length
    matching - a tuple of single nodes, tuples, or NoneTypes
               the argument list must match this restriction
               if a position is None, then
    """
    if length is not None:
        if len(args) != length:
            return (False, "length (%d) does not equal %d" % (len(args), length,) )
    
    matched = 0
    if match is not None:
        for constraint, (arg_index, arg) in zip(match, enumerate(args)):
            if constraint is None:
                pass
            
            elif isinstance(constraint, tuple) or issubclass(constraint, DBNBaseNode):
                matched += 1
                return assert_node(arg, matches=constraint, node_name ="arg %d" % arg_index)
                    
            else:
                raise ValueError("BAD CONSTRAINT, LOUIS")
    
    return (True, None)
    
def assert_node(node, matches=None, node_name=None):
    """
    asserts that the given node is one of the given types
    (types can be a tuple or just one type)
    raises a louiserror if types is bad,
    returns False if the node is bad
    returns true otherwise
    """
    if node_name is None:
        node_name = node.display_name
    
    if matches is None:
        pass

    elif isinstance(matches, tuple):
        # lets make sure every type in the tuple is a subclass of BaseNode
        if not all(issubclass(t, DBNBaseNode) for t in matches):
            raise ValueError("Louis... bad type in contraint tuple!")
        
        if not isinstance(node, matches):
            return (False, "%s is not a %s" % (node_name, ', nor a '.join(c.display_name for c in matches)))
    
    elif issubclass(matches, DBNBaseNode):
        if not isinstance(node, matches):
            return (False, "%s is not a %s" % (node_name, constraint.display_name))
    
    else:
        raise ValueError("Bad constraint type!")
        
    return (True, None)
    
def strip_newline(tokens):
    """
    from the given token set.
    mutates.
    """
    last_token = tokens[-1]
    if last_token.type == 'NEWLINE':
        tokens.pop()
    return tokens
    

class DBNParser:
    def parse(self, tokens):
        return parse_block(tokens, top_level=True)
