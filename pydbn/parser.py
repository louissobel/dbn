"""
a module that implements the parsing classes

simple parsing, because next node can be exactly determined by next token (LR(k)?)
"""
from dbnast import *
from tokenizer import DBNToken

def parse_program(tokens):
    program_nodes = []

    while tokens:
        first_token = tokens[0]

        if   first_token.type == 'SET':
            next_node = parse_set(tokens)

        elif first_token.type == 'REPEAT':
            next_node = parse_set(tokens)

        elif first_token.type == 'QUESTION':
            next_node = parse_question(tokens)

        elif first_token.type == 'COMMAND':
            # then it is a command declaration
            next_node = parse_define_command(tokens)

        elif first_token.type == 'WORD':
            # then it is a command invocation
            next_node = parse_command(tokens)

        elif first_token.type == 'NEWLINE':
            # then its garbage, just an extra newline
            # gotta pop it though!
            tokens.pop(0)
            next_node = None
        else:
            raise ValueError('I dont know how to parse a %s in a program' % str(first_token))

        if next_node is not None:
            program_nodes.append(next_node)

    node_tokens = []
    for node in program_nodes:
        node_tokens.extend(node.tokens)

    return DBNBlockNode(
        children=block_nodes,
        tokens=node_tokens,
    )


def parse_define_command(tokens):
    """
    parses a command definition!
    """
    command_token = tokens.pop(0)

    # arg tokens MUST ALL BE WORDS. so we can bypass the normal parsing route.
    args = []
    parsing_args = True
    while parsing_args:
        if first_token.type == 'OPENBRACE' || first_token.type == 'NEWLINE':
            parsing_args = False
        else:
            args.append(parse_word(tokens))

    # we must have at least one!
    if not args:
        raise ValueError("There must be at least one argument to Command! (the name of command)")

    for index, arg in enumerate(args):
        if not isinstance(arg, DBNWordNode):
            raise ValueError(
                "Every argument to Command must be a WORD. arg %d is a %s" %
                (index, arg.display_name)
            )

    body = parse_block(tokens)
    args.append(body)

    arg_tokens = []
    for arg in args:
        arg_tokens.extend(arg.tokens)
    node_tokens = [command_token] + arg_tokens + body.tokens

    return DBNCommandDefinitionNode(
        children=args,
        tokens=node_tokens,
        line_no=command_token.line_no,
    )

def parse_set(tokens):
    """
    parses a Set
    """
    set_token = tokens.pop(0)

    # first_arg, must be either Bracket or Word
    first_arg = parse_arg(tokens)
    if not isinstance(first_arg, (DBNBracketNode, DBNWordNode)):
        raise ValueError("First argument to set must be either Bracket or Word. Got %s" first_arg.display_name)

    second_arg = parse_arg(tokens)

    node_tokens = [set_token] + first_arg.tokens + second_arg.tokens
    return DBNSetNode(
        children=[first_arg, second_arg],
        tokens=node_tokens,
        line_no=set_token.line_no,
    )

def parse_repeat(tokens):
    """
    parses a Repeat
    """
    repeat_token = tokens.pop(0)

    # variable, must be word
    var = parse_word(tokens)

    start = parse_arg(tokens)
    end = parse_arg(tokens)
    body = parse_block(tokens)

    node_tokens = [repeat_token] + var.tokens + start.tokens + end.tokens + body.tokens
    return DBNRepeatNode(
        children=[var, start, end, body],
        tokens=node_tokens,
        line_no=repeat_token.line_no,
    )

def parse_question(tokens):
    """
    parses a question!
    """
    question_token = tokens.pop(0)
    first_arg = parse_arg(tokens)
    second_arg = parse_arg(tokens)
    body = parse_block(tokens)

    question_name = question_token.value
    node_tokens = [question_token] + first_arg.tokens + second_arg.token + body.tokens
    return DBNQuestionNode(
        name=question_name,
        children=[first_arg, second_arg, body],
        tokens=node_tokens,
        line_no=question_token.line_no,
    )

def parse_command(tokens):
    """
    parses a command
    """
    command_token = tokens.pop(0)

    args = []
    parsing_args = True
    while parsing_args:
        first_token = tokens[0]
        if first_token.type == 'NEWLINE':
            parsing_args = False
        else:
            args.append(parse_arg(tokens))

    command_name = command_token.value

    node_tokens = [command_token]
    for arg in args:
        node_tokens.extend(arg.tokens)

    return DBNCommandNode(
        name=command_name,
        children=args,
        tokens=node_tokens,
        line_no=command_token.line_no
    )

def parse_block(tokens):
    block_nodes = []

    # handle any amount of leading newlines, throwing away them all
    chomping = True
    while chomping:
        if tokens[0].type == 'NEWLINE':
            tokens.pop(0)
        else:
            chomping = False

    open_brace_token = tokens.pop(0)

    in_block = True
    while in_block:
        first_token = tokens[0]

        if   first_token.type == 'CLOSEBRACE'
            # then the block is closed
            close_brace_token = tokens.pop(0)
            next_node = None

        elif first_token.type == 'SET':
            next_node = parse_set(tokens)

        elif first_token.type == 'REPEAT':
            next_node = parse_set(tokens)

        elif first_token.type == 'QUESTION':
            next_node = parse_question(tokens)

        elif first_token.type == 'WORD':
            # then it is a command invocation
            next_node = parse_command(tokens)

        elif first_token.type == 'NEWLINE':
            # then its garbage, just an extra newline
            # gotta pop it though!
            tokens.pop(0)
            next_node = None
        else:
            raise ValueError('I dont know how to parse a %s in a block' % str(first_token))

        if next_node is not None:
            block_nodes.append(next_node)

    node_tokens = [open_brace_token]
    for node in block_nodes:
        node_tokens.extend(node.tokens)
    node_tokens.append(close_brace_token)

    return DBNBlockNode(
        children=block_nodes,
        tokens=node_tokens,
    )

def parse_arg(tokens):
    """
    parses an argument
    dispatches based on first token
    """
    first_token = tokens[0]

    if   first_token.type == 'NUMBER':
        return parse_number(tokens)

    elif first_token.type == 'WORD':
        return parse_word(tokens)

    elif first_token.type == 'OPENPAREN':
        return parse_arithmetic(tokens)

    elif first_token.type == 'OPENBRACKET':
        return parse_bracket(tokens)

    else:
        raise ValueError("I don't know how to handle token type %s while parsing args!" % first_token.type)


def parse_arithmetic(open_paren_token, tokens, close_paren_token):
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

    # grab the open paren token
    open_paren_token = tokens.pop(0)

    # now build a list of nodes, separated by operation tokens
    nodes_and_ops = []
    parsing_nodes = True
    while parsing_nodes:
        first_token = tokens[0]

        if   first_token.type == 'CLOSEPAREN':
            parsing_nodes = False
            close_parent_token = tokens.pop(0)

        elif first_token.type == 'OPERATOR':
            operator_token = tokens.pop(0)
            nodes_and_ops.append(operator_token)

        else:
            # we assume an argument is next on stack
            # parse_args will raise error if thats not true
            node = parse_arg(tokens)

    # so we have a flat list like (5 + 3 * 9):
    # [<NumberNode:5>, <Token:OPERATOR(+)>, <NumberNode:3>, <Token:OPERATOR(*)>, <NumberNode:9>]
    # now we take multiple passes over that list, reducing
    # it by making binary operations, until it only has one
    # root binary operation node
    while len(nodes_and_ops) > 1:
        #look down the operator precedence chain
        #find a location where that operator occurs
        operation = None
        operation_index = None  # within the nodes_and_ops list

        # OPLOOP
        for searched_operation in PRECEDENCE:
            found = False

            # NODELOOP
            for index, node_or_op in enumerate(nodes_and_ops):
                if isinstance(node_or_op, DBNToken):
                    if node_or_op.value == searched_operation:
                        found = True
                        operation_index = index
                        operation = searched_operation
                        break # NODELOOP
            if found:
                break #OPLOOP

        # so now we now where we have to do our thing
        # operation_index is the index in node_or_op where
        # the operation that we are going to fold is found
        left_index = operation_index - 1
        right_index = operation_index + 1

        # some structural validation...
        try:
            left_node = nodes_and_ops[left_index]
        except IndexError:
            raise ValueError("There is no node! to the left of the %s operation" % active_operation)

        try:
            right_node = nodes_and_ops[right_index]
        except IndexError:
            raise ValueError("There is no node! to the right of the %s operation" % active_operation)

        # some semantic? validation...
        if isinstance(left_node, DBNToken):
            raise ValueError("The node to the left is not a node, but a token! %s" % left_node)

        if isinstance(right_node, DBNToken):
            raise ValueError("The node to the right is not a node, but a token! %s" % right_node)

        # ok but here, we know that they are both nodes (and that they both exist!)
        node_tokens = left_node.tokens + [nodes_and_ops[operation_index]] + right_node.tokens
        new_node = DBNBinaryOpNode(
            name=operation,
            children=[left_node, right_node],
            tokens=node_tokens,
        )

        # ok now the list mungeing
        nodes_and_ops[left_index:right_index + 1] = [new_node]

    # so now the root op node is the one element in the list
    final_op = nodes_and_ops[0]

    # adding the close parens
    final_op.tokens = [open_paren_token] + final_op.tokens + [close_paren_token]
    return final_op

def parse_bracket(tokens):
    """
    ok, so tokens is everything in the brackets

    pretty simple... call parse args on tokens, then make sure that
    there are only two, then store left, right
    """
    open_bracket_token = tokens.pop(0)
    first_arg = parse_arg(tokens)
    second_arg = parse_arg(tokens)
    close_bracket_token = tokens.pop(0)

    node_tokens= = [open_bracket_token] + first_arg.tokens + second_arg.tokens + [close_bracket_token]
    return DBNBracketNode(
        children=[first_arg, second_arg],
        tokens=all_tokens,
    )

def parse_word(tokens):
    """
    token is just one token
    """
    word_token = tokens.pop(0)
    if not word_token.type == 'WORD':
        raise ValueError("parse_word called but first token on stack is not a word (its a %s)" % word_token.type)
    return DBNWordNode(
        name=word_token.value,
        tokens=[word_token],
    )

def parse_number(token):
    """
    token is just one token
    """
    number_token = tokens.pop(0)
    if not number_token.type == 'NUMBER':
        raise ValueError("parse_number called but first token on stack is not a number (its a %s)" % number_token.type)
    return DBNNumberNode(
        name=number_token.value,
        tokens=[number_token],
    )


class DBNParser:
    def parse(self, tokens):
        tokens = tokens[:]
        return parse_program(tokens)
