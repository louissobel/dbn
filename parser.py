"""
a module that implements the parsing classes
"""


from ast import *

          
def parse_until_next(tokens, token_type):
    """
    will return a list of tokens unit the next
    one of type token_type or the end of the list
    """
    out_tokens = []
    while tokens:
        next_token = tokens.pop(0)
        if next_token.type == token_type:
            break
        else:
            out_tokens.append(next_token)
    return out_tokens
    
def parse_until_balanced(tokens, left_type, right_type):
    """
    will parse until a balance is found
    
    assumes that there is already a score of 1 (one open)
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
             
def parse(tokens):
    return parse_block(tokens[:])
    
def parse_block(tokens):
    
    # only a couple of options.
    # actually, only option is that is is a command
    # also, we are assuming that the closing bracket is not included        
    node = DBNBlockNode()
    while tokens:        
        peek_token = tokens[0]
        # word
        # command
        # newline
        if peek_token.type == 'SET':
            set_tokens = parse_until_next(tokens, 'NEWLINE')
            set_node = parse_set(set_tokens)
            node.add_child(set_node)
            
        elif peek_token.type == 'REPEAT':
            arg_tokens = parse_until_next(tokens, 'OPENBRACE')
            body_tokens = parse_until_balanced(tokens, 'OPENBRACE', 'CLOSEBRACE')
            repeat_node = parse_repeat(arg_tokens, body_tokens)
            node.add_child(repeat_node)
        
        elif peek_token.type == 'WORD':
            # then we treat it as a command
            command_tokens = parse_until_next(tokens, 'NEWLINE')
            
            #print [str(s) for s in command_tokens]
            
            command_node = parse_command(command_tokens)
            node.add_child(command_node)
            
        elif peek_token.type == 'NEWLINE':
            # then it is just an extra blank new line...
            # and we throw it away
            tokens.pop(0)
            
        else:
            raise ValueError('I dont know how to parse a %s in a block' % str(peek_token))
    
    return node

def parse_command(tokens):
    command_token = tokens.pop(0)
    
    if not command_token.type == 'WORD':
        raise ValueError("Expected a WORD, but got a %s while parsing command" % command_token.type)
    
    args = parse_args(tokens)
    return DBNCommandNode(command_token.value, args)
    
def parse_set(tokens):
    """
    set is special... because first arg can only be DBNBracketNode
    """
    set_token = tokens.pop(0)
    args = parse_args(tokens)
    
    if len(args) != 2:
        raise ValueError("Must have two args to Set")
    
    if not isinstance(args[0], (DBNBracketNode, DBNWordNode)):
        raise ValueError("First argument to set must be [] or variable")
    
    return DBNSetNode(args[0], args[1])
            
def parse_repeat(arg_tokens, body_tokens):
    """
    parses a repeat
    """
    repeat_token = arg_tokens.pop(0)
    
    # the newline before the block is optional.
    # if it there, we need to remove it
    # if it is not there, we are OK
    try:
        last_arg_token = arg_tokens[-1]
        if last_arg_token.type == 'NEWLINE':
            # then we pop it away
            arg_tokens.pop()
        else:
            # we do nothing
            pass
            
    except IndexError:
        raise ValueError("arg_tokens passed to parse_repeat cannot be empty")
    

    args = parse_args(arg_tokens)
    
    # wee need three!
    if len(args) != 3:
        raise ValueError("there must be three arguments (besides the block) to repeat!")
    
    # the first one must be a word
    if not isinstance(args[0], DBNWordNode):
        raise ValueError("first argument to repeat must be a Word!")
    
    body = parse_block(body_tokens)
    
    var = args[0]
    start = args[1]
    end = args[2]
    
    return DBNRepeatNode(var, start, end, body)
    
    
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
        
        # i know how to handle NUMBER, WORD, OPENGROUP ( and OPENGROUP [
        if first_token.type == 'NUMBER':
            arg_list.append(parse_number(first_token))
        
        elif first_token.type == 'WORD':
            arg_list.append(parse_word(first_token))
            
        elif first_token.type == 'OPENPAREN':
            arithmetic_tokens = parse_until_balanced(tokens, 'OPENPAREN', 'CLOSEPAREN')
            arg_list.append(parse_arithmetic(arithmetic_tokens))
        
        elif first_token.type == 'OPENBRACKET':
            bracket_tokens = parse_until_balanced(tokens, 'OPENBRACKET', 'CLOSEBRACKET')
            arg_list.append(parse_bracket(bracket_tokens))
            
        else:
            raise ValueError("I don't know how to handle token type %s while parsing args!" % first_token.type)
            
    return arg_list

def parse_bracket(tokens):
    """
    ok, so tokens is everything in the brackets
    
    pretty simple... call parse args on tokens, then make sure that
    there are only two, then store left, right
    """
    args = parse_args(tokens)
    if len(args) > 2:
        raise ValueError("Too many arguments inside of a bracket, only 2!")
    
    if len(args) < 2:
        raise ValueError("Too few arguments inside of a bracket.. must have 2!")
    
    # so we know its 2
    left = args[0]
    right = args[1]
    
    return DBNBracketNode(left, right)
    
def parse_arithmetic(tokens):
    PRECEDENCE = ['*', '/', '-', '+'] # ok?
    
    # so algorithm:
    # we walk down to precedence levels, looking for things.
    # if we find one, look for its left,
    # and its right, combine them!
    nodes_and_ops = []
    while tokens:
        first_token = tokens.pop(0)
        if first_token.type == 'WORD':
            nodes_and_ops.append(parse_word(first_token))
        
        elif first_token.type == 'NUMBER':
            nodes_and_ops.append(parse_number(first_token))
        
        elif first_token.type == 'OPENPAREN':
            arithmetic_tokens = parse_until_balanced(tokens, 'OPENPAREN', 'CLOSEPAREN')
            nodes_and_ops.append(parse_arithmetic(arithmetic_tokens))
        
        elif first_token.type == 'OPENBRACKET':
            bracket_tokens = parse_until_balanced(tokens, 'OPENBRACKET', 'CLOSEBRACKET')
            nodes_and_ops.append(parse_bracket(bracket_tokens))
            
        elif first_token.type == 'OPERATOR':
            nodes_and_ops.append(first_token.value)
            
    
    while len(nodes_and_ops) > 1:
        #look down the precedence chain
        #find a location where it occurs
        active_operation = ''
        active_index = 0
        for operation in PRECEDENCE:
            active_operation = operation
            active_index = 0
            found = False
            while active_index < len(nodes_and_ops):
                if nodes_and_ops[active_index] == operation:
                    found = True
                    break
                active_index += 1
            if found:
                break
                
        # so now we now where we have to do our thing
        # index
        left_index = active_index - 1
        right_index = active_index + 1
        
        try:
            left_node = nodes_and_ops[left_index]
        except IndexError:
            raise ValueError("There is no node! to the left of the %s operation" % active_operation)
            
        try:
            right_node = nodes_and_ops[right_index]
        except IndexError:
            raise ValueError("There is no node! to the right of the %s operation" % active_operation)
        
        if isinstance(left_node, basestring):
            raise ValueError("The node to the left is not a node, but a string! %s" % left_node)
            
        if isinstance(right_node, basestring):
            raise ValueError("The node to the right is not a node, but a string! %s" % right_node)
            
        # ok but here, we know that they are both nodes
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
    
    
class DBNParser:
    def parse(self, tokens):
        return parse_block(tokens)
