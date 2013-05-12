"""
a module that implements the parsing classes

simple parsing, because next node can be exactly determined by next token and current node (LL(1)?)
"""
import operator

from structures.ast_nodes import *
from structures import DBNToken

def parse(tokens):
    """
    destroyes tokens
    """
    return parse_program(tokens)

def parse_program(tokens):
    """
    parses a DBN program
    """
    program_nodes = []

    while tokens:
        first_token = tokens[0]

        if   first_token.type == 'COMMAND':
            # then it is a command declaration
            next_node = parse_define_command(tokens)

        elif first_token.type == 'LOAD':
            next_node = parse_load(tokens)

        else:
            next_node = parse_block_statement(tokens)

        if next_node is not None:
            program_nodes.append(next_node)

    node_tokens = []
    for node in program_nodes:
        node_tokens.extend(node.tokens)

    return DBNProgramNode(
        children=program_nodes,
        tokens=node_tokens,
    )

def parse_define_command(tokens):
    """
    parses a command definition!
    """
    command_token = tokens.pop(0)

    # Arg tokens MUST ALL BE WORDS. so we can bypass the normal parsing route.
    children = []
    parsing_args = True
    while parsing_args:
        first_token = tokens[0]

        if first_token.type == 'OPENBRACE' or first_token.type == 'NEWLINE':
            # marks the end of the formal args; parse_block will handle this tokens
            parsing_args = False
        else:
            try:
                children.append(parse_word(tokens))
            except ValueError:
                # Then parse_word couldn't handle the stack
                raise ValueError("Every argument to Command must be a word!")

    # we must have at least one!
    if not children:
        raise ValueError("There must be at least one argument to Command! (the name of command)")

    body = parse_block(tokens)

    noop = parse_newline(tokens)

    children.append(body)

    child_tokens = []
    for child in children:
        child_tokens.extend(child.tokens)

    # child_tokens included the tokens of the body
    node_tokens = [command_token] + child_tokens + noop.tokens

    return DBNCommandDefinitionNode(
        children=children,
        tokens=node_tokens,
        line_no=command_token.line_no,
    )

def parse_load(tokens):
    load_token = tokens.pop(0)

    # next token must be path
    path_token = tokens.pop(0)
    if not path_token.type == 'PATH':
        raise ValueError("PATH token must be after LOAD (its a %s)" % path_token.type)

    noop = parse_newline(tokens)

    node_tokens = [load_token] + [path_token] + noop.tokens
    return DBNLoadNode(
        value=path_token.value,
        tokens=node_tokens,
        line_no=load_token.line_no,
    )


def parse_block(tokens):
    block_nodes = []

    # handle any amount of leading newlines, storing them
    chomping = True
    leading_newline_tokens = []
    while chomping:
        if tokens[0].type == 'NEWLINE':
            leading_newline_tokens.append(tokens.pop(0))
        else:
            chomping = False

    open_brace_token = tokens.pop(0)

    # assert that the next token is a NEWLINE
    if not tokens[0].type == 'NEWLINE':
        raise ValueError('block open brace must be followed by newline')

    in_block = True
    while in_block:
        first_token = tokens[0]

        if   first_token.type == 'CLOSEBRACE':
            # then the block is closed
            close_brace_token = tokens.pop(0)
            in_block = False

        else:
            next_node = parse_block_statement(tokens)
            block_nodes.append(next_node)

    node_tokens = leading_newline_tokens + [open_brace_token]
    for node in block_nodes:
        node_tokens.extend(node.tokens)
    node_tokens.append(close_brace_token)

    return DBNBlockNode(
        children=block_nodes,
        tokens=node_tokens,
    )

def parse_block_statement(tokens):
    """
    Parses one statement out from tokens
    Set, Repeat,  Question, Word (command invocation)
    will raise an error if unable to build a statement

    Also handles extra newlines by popping them and returning None
    Could handle newlines by having a DBNNoOpNode, which is a NOOP
    Would remove necessity of checking if return value is None. Hmmm

    Each statement is responsbile for ensuring that it ends with a new line
    and that that newline is popped from the token stack
    """
    first_token = tokens[0]

    if   first_token.type == 'SET':
        return parse_set(tokens)

    elif first_token.type == 'REPEAT':
        return parse_repeat(tokens)

    elif first_token.type == 'QUESTION':
        return parse_question(tokens)

    elif first_token.type == 'WORD':
        # then it is a command invocation
        return parse_command(tokens)

    elif first_token.type == 'NEWLINE':
        # then it is just an extra newline (noop)
        return parse_newline(tokens)


    else:
        raise ValueError("I don't know how to parse %s as a statement!" % first_token.type)

def parse_set(tokens):
    """
    parses a Set
    """
    set_token = tokens.pop(0)

    # first_arg, must be either Bracket or Word
    first_arg = parse_arg(tokens)
    if not isinstance(first_arg, (DBNBracketNode, DBNWordNode)):
        raise ValueError("First argument to set must be either Bracket or Word. Got %s" % first_arg)

    second_arg = parse_arg(tokens)

    noop = parse_newline(tokens)

    node_tokens = [set_token] + first_arg.tokens + second_arg.tokens + noop.tokens
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
    # parse word will throw error for us
    var = parse_word(tokens)

    start = parse_arg(tokens)
    end = parse_arg(tokens)
    body = parse_block(tokens)

    noop = parse_newline(tokens)

    node_tokens = [repeat_token] + var.tokens + start.tokens + end.tokens + body.tokens + noop.tokens
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

    noop = parse_newline(tokens)

    question_name = question_token.value
    node_tokens = [question_token] + first_arg.tokens + second_arg.tokens + body.tokens + noop.tokens
    return DBNQuestionNode(
        value=question_name,
        children=[first_arg, second_arg, body],
        tokens=node_tokens,
        line_no=question_token.line_no,
    )

def parse_command(tokens):
    """
    parses a command
    """
    command_token = tokens.pop(0)
    # assuming it is a WORD based on parse contract

    args = []
    parsing_args = True
    while parsing_args:
        try:
            first_token = tokens[0]
        except IndexError:
            raise ValueError("Unterminated Command!")

        if first_token.type == 'NEWLINE':
            parsing_args = False
            noop = parse_newline(tokens)
        else:
            args.append(parse_arg(tokens))

    command_name = command_token.value

    node_tokens = [command_token]
    for arg in args:
        node_tokens.extend(arg.tokens)
    node_tokens += noop.tokens

    return DBNCommandNode(
        value=command_name,
        children=args,
        tokens=node_tokens,
        line_no=command_token.line_no
    )

def parse_newline(tokens):
    """
    returns a noop if its a newline
    """
    first_token = tokens[0]
    if not first_token.type == 'NEWLINE':
        raise ValueError("parse_newline called without newline as first token (%s)" % first_token.type)

    newline_token = tokens.pop(0)
    return DBNNoopNode(tokens=[newline_token])


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

def parse_arithmetic(tokens):
    """
    parse a set of tokens representing 'arithmetic'
    triggered by an open parenthesis

    parses using Dijkstras shunting yard
    """
    PRECEDENCE = {
        '+' : (0, 'LEFT'),
        '-' : (0, 'LEFT'),
        '*' : (1, 'LEFT'),
        '/' : (1, 'LEFT')
    }

    # grab the open paren token
    open_paren_token = tokens.pop(0)

    # Shunting yard algorithm for precedence parsing
    # http://en.wikipedia.org/wiki/Shunting-yard_algorithm
    output_stack = []
    op_stack = []

    # Functions for managing the output stack
    def add_op(op_token):
        try:
            right = output_stack.pop()
            left = output_stack.pop()
        except IndexError:
            raise ValueError('Not enough operands for %s!' % op_token.value)

        node_tokens = left.tokens + [op_token] + right.tokens
        new_node = DBNBinaryOpNode(
            value=op_token.value,
            children=[left, right],
            tokens=node_tokens,
        )
        output_stack.append(new_node)

    parsing = True
    while parsing:
        first_token = tokens[0]

        if  first_token.type == 'CLOSEPAREN':
            parsing = False
            close_paren_token = tokens.pop(0)

        elif first_token.type == 'OPERATOR':
            op_token = tokens.pop(0)
            precedence, assoc = PRECEDENCE[op_token.value]

            while op_stack:
                top_precedence, _ = PRECEDENCE[op_stack[-1].value]
                compare = operator.gt if assoc == 'LEFT' else operator.ge
                if compare(precedence, top_precedence):
                    break
                else:
                    add_op(op_stack.pop())

            # Now append this token to the op_stack
            op_stack.append(op_token)

        else:
            # We assume an argument is next on stack
            output_stack.append(parse_arg(tokens))

    # finish it up
    while op_stack:
        add_op(op_stack.pop())

    # if result_stack is greater than one, we have problems
    if len(output_stack) > 1:
        raise ValueError("Bad arithmetic!")

    # so now the root op node is the one element in the list
    final_op = output_stack[0]

    # adding the parenthesis tokens
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

    node_tokens = [open_bracket_token] + first_arg.tokens + second_arg.tokens + [close_bracket_token]
    return DBNBracketNode(
        children=[first_arg, second_arg],
        tokens=node_tokens,
    )

def parse_word(tokens):
    """
    token is just one token
    """
    word_token = tokens.pop(0)
    if not word_token.type == 'WORD':
        raise ValueError("parse_word called but first token on stack is not a word (its a %s)" % word_token.type)
    return DBNWordNode(
        value=word_token.value,
        tokens=[word_token],
    )

def parse_number(tokens):
    """
    token is just one token
    """
    number_token = tokens.pop(0)
    if not number_token.type == 'NUMBER':
        raise ValueError("parse_number called but first token on stack is not a number (its a %s)" % number_token.type)
    return DBNNumberNode(
        value=number_token.value,
        tokens=[number_token],
    )
