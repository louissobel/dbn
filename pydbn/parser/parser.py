"""
a module that implements the parsing classes

simple parsing, because next node can be exactly determined by next token and current node (LL(1)?)
"""
import operator

from .structures.ast_nodes import *
from .structures import DBNToken, ParseError

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
        first_token = peek_asserting_present(tokens)

        if   first_token.type in ('COMMAND', 'NUMBERDEF'):
            # then it is a procedure definition
            next_node = parse_define_procedure(tokens)

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

def parse_define_procedure(tokens):
    """
    parses a procedure definition
    """
    procedure_def_token = pop_asserting_present(tokens)

    # Arg tokens MUST ALL BE WORDS. so we can bypass the normal parsing route.
    children = []
    parsing_args = True
    while parsing_args:
        first_token = tokens[0]

        if first_token.type == 'OPENBRACE' or first_token.type == 'NEWLINE':
            # marks the end of the formal args; parse_block will handle this token
            parsing_args = False
        else:
            if first_token.type != 'WORD':
                raise ParseError(
                    "Every argument to a %s definition needs to be a variable name, got \"%s\"" % (
                        procedure_def_token.value,
                        first_token.value,
                    ),
                    first_token.line_no,
                    first_token.char_no,
                )

            children.append(parse_word(tokens))

    # we must have at least one!
    if not children:
        raise ParseError(
            "%s definition requires at least one argument (the name of the new %s), but none provided" % (
                procedure_def_token.value,
                procedure_def_token.value,
            ),
            procedure_def_token.line_no,
            procedure_def_token.char_no,
        )

    body = parse_block(tokens, block_owning_token=procedure_def_token)

    children.append(body)

    child_tokens = []
    for child in children:
        child_tokens.extend(child.tokens)

    proc_type = 'command' if procedure_def_token.type == 'COMMAND' else 'number'

    # child_tokens includes the tokens of the body
    node_tokens = [procedure_def_token] + child_tokens

    return DBNProcedureDefinitionNode(
        children=children,
        tokens=node_tokens,
        line_no=procedure_def_token.line_no,
        value=proc_type,
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

def parse_block(tokens, block_owning_token=None):
    block_nodes = []

    # handle any amount of leading newlines, storing them
    # TODO: should we really handle _any_ amount of newlines? or just 0 or 1?
    chomping = True
    leading_newline_tokens = []
    while chomping:
        if not tokens:
            raise_unexpected_block_start_end_of_input(block_owning_token)

        if peek_asserting_present(tokens).type == 'NEWLINE':
            leading_newline_tokens.append(pop_asserting_present(tokens))
        else:
            chomping = False

    open_brace_token = pop_asserting_present(tokens)
    if open_brace_token.type != 'OPENBRACE':
        raise_unexpected_block_opening_token(block_owning_token, open_brace_token)


    validate_is_newline(
        peek_asserting_present(tokens),
        "\"{\" must be followed by a newline to define a block",
    )

    in_block = True
    while in_block:
        if not tokens:
            raise_unexpected_block_end_end_of_input(block_owning_token)

        first_token = peek_asserting_present(tokens)

        if   first_token.type == 'CLOSEBRACE':
            # then the block is closed
            close_brace_token = pop_asserting_present(tokens)
            in_block = False

        else:
            next_node = parse_block_statement(tokens)
            block_nodes.append(next_node)

    validate_is_newline(
        peek_asserting_present(tokens),
        "The closing \"}\" of a block must be followed by a newline",
    )
    trailing_newline_token = pop_asserting_present(tokens)

    node_tokens = leading_newline_tokens + [open_brace_token]
    for node in block_nodes:
        node_tokens.extend(node.tokens)
    node_tokens.append(close_brace_token)
    node_tokens.append(trailing_newline_token)

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
    first_token = peek_asserting_present(tokens)

    if   first_token.type == 'SET':
        return parse_set(tokens)

    elif first_token.type == 'REPEAT':
        return parse_repeat(tokens)

    elif first_token.type == 'QUESTION':
        return parse_question(tokens)

    elif first_token.type == 'WORD':
        # then it is a command invocation
        return parse_command_call(tokens)

    elif first_token.type == 'VALUE':
        return parse_value(tokens)

    elif first_token.type == 'OPENBRACE':
        return parse_block(tokens, block_owning_token=first_token)

    elif first_token.type == 'NEWLINE':
        # then it is just an extra newline (noop)
        return parse_newline(tokens)

    elif first_token.type in ('COMMAND', 'NUMBERDEF'):
        raise ParseError(
            "%s definitions can only be at the top level of the program" % first_token.value,
            first_token.line_no,
            first_token.char_no,
        )

    else:
        raise ParseError(
            "Lines should begin with a command (Line, Pen, Paper, Set, etc) — saw \"%s\"" % (first_token.value),
            first_token.line_no,
            first_token.char_no,
        )

def parse_set(tokens):
    """
    parses a Set
    """
    set_token = pop_asserting_present(tokens)

    # first_arg, must be either Bracket or Word
    next_token = peek_asserting_present(tokens)
    validate_not_newline(
        next_token,
        "Set needs to be passed two arguments, but none provided",
    )

    global_token = None
    if next_token.type   == 'OPENBRACKET':
        first_arg = parse_bracket(tokens)
        set_type = 'dot'

    elif next_token.type == 'WORD':
        first_arg = parse_word(tokens)
        set_type = 'variable'

    elif next_token.type == 'GLOBAL':
        global_token = pop_asserting_present(tokens)
        next_token = peek_asserting_present(tokens)
        if next_token.type != 'WORD':
            raise ParseError(
                "Set \"global\" must be followed by variable name",
                next_token.line_no,
                next_token.char_no,
            )
        first_arg = parse_word(tokens)
        set_type = 'global_variable'

    else:
        raise ParseError(
            "First argument to Set must be either a [x y] dot or a variable, but got \"%s\"" % next_token.value,
            next_token.line_no,
            next_token.char_no
        )

    validate_not_newline(
        peek_asserting_present(tokens),
        "Set needs to be passed two arguments, but only one provided",
    )
    second_arg = parse_arg(tokens)

    next_token = peek_asserting_present(tokens)
    validate_is_newline(
        peek_asserting_present(tokens),
        "Set can only be passed two arguments, but got extra"
    )
    noop = parse_newline(tokens)

    node_tokens = [set_token]
    if global_token:
        node_tokens.append(global_token)

    node_tokens += first_arg.tokens + second_arg.tokens + noop.tokens
    return DBNSetNode(
        value=set_type,
        children=[first_arg, second_arg],
        tokens=node_tokens,
        line_no=set_token.line_no,
    )

def parse_repeat(tokens):
    """
    parses a Repeat
    """
    repeat_token = pop_asserting_present(tokens)

    # Variable
    next_token = peek_asserting_present(tokens)
    validate_not_newline(
        next_token,
        "Repeat needs to be passed three arguments, but none provided",
    )
    if next_token.type != 'WORD':
        raise ParseError(
            "The first argument to Repeat must be the name of a variable, got \"%s\"" % next_token.value,
            next_token.line_no,
            next_token.char_no,
        )
    var = parse_word(tokens)

    validate_not_newline(
        peek_asserting_present(tokens),
        "Repeat needs to be passed three arguments, but only one provided",
    )
    start = parse_arg(tokens)

    validate_not_newline(
        peek_asserting_present(tokens),
        "Repeat needs to be passed three arguments, but only two provided",
    )
    end = parse_arg(tokens)

    body = parse_block(tokens, block_owning_token=repeat_token)

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
    question_token = pop_asserting_present(tokens)

    validate_not_newline(
        peek_asserting_present(tokens),
        "%s? needs to be passed two arguments, but got none" % question_token.value,
    )
    first_arg = parse_arg(tokens)

    validate_not_newline(
        peek_asserting_present(tokens),
        "%s? needs to be passed two arguments, but got only one" % question_token.value,
    )
    second_arg = parse_arg(tokens)

    body = parse_block(tokens, block_owning_token=question_token)

    question_name = question_token.value
    node_tokens = [question_token] + first_arg.tokens + second_arg.tokens + body.tokens
    return DBNQuestionNode(
        value=question_name,
        children=[first_arg, second_arg, body],
        tokens=node_tokens,
        line_no=question_token.line_no,
    )

def parse_command_call(tokens):
    """
    parses a command call
    """
    command_name = parse_word(tokens)

    args = []
    parsing_args = True
    while parsing_args:
        first_token = peek_asserting_present(tokens)

        if first_token.type == 'NEWLINE':
            parsing_args = False
            noop = parse_newline(tokens)
        else:
            args.append(parse_arg(tokens))

    node_tokens = command_name.tokens[:]
    for arg in args:
        node_tokens.extend(arg.tokens)
    node_tokens += noop.tokens

    return DBNProcedureCallNode(
        value='command',
        children=[command_name] + args,
        tokens=node_tokens,
        line_no=command_name.tokens[0].line_no
    )

def parse_value(tokens):
    """
    parses a Value statement

    semantic validation (Value only in command def)
    occurs at compile-time, not parse
    """
    value_token = pop_asserting_present(tokens)

    validate_not_newline(
        peek_asserting_present(tokens),
        "Value needs one argument, but got none"
    )
    arg = parse_arg(tokens)

    validate_is_newline(
        peek_asserting_present(tokens),
        "Value can only be passed one argument, got extra"
    )
    noop = parse_newline(tokens)

    node_tokens = [value_token] + arg.tokens + noop.tokens
    return DBNValueNode(
        children=[arg],
        tokens = node_tokens,
        line_no=value_token.line_no
    )

def parse_newline(tokens):
    """
    returns a noop if its a newline
    """
    first_token = tokens[0]
    if not first_token.type == 'NEWLINE':
        raise AssertionError("parse_newline called without newline as first token (%s)" % first_token.type)

    newline_token = tokens.pop(0)
    return DBNNoopNode(tokens=[newline_token])


def parse_arg(tokens):
    """
    parses an argument
    dispatches based on first token
    """
    first_token = tokens[0]

    validate_not_newline(
        first_token,
        "Unexpected end of line while processing number, maybe a missing closing \")\", \"]\", or \">\"",
    )

    if   first_token.type == 'NUMBER':
        return parse_number(tokens)

    elif first_token.type == 'WORD':
        return parse_word(tokens)

    elif first_token.type == 'OPENPAREN':
        return parse_arithmetic(tokens)

    elif first_token.type == 'OPENBRACKET':
        return parse_bracket(tokens)

    elif first_token.type == 'OPENANGLEBRACKET':
        return parse_number_call(tokens)

    ## Error cases
    elif first_token.type == 'OPERATOR':
        raise ParseError(
            "Math operator \"%s\" needs to be wrapped in parentheses" % first_token.value,
            first_token.line_no,
            first_token.char_no,
        )
    elif first_token.type == 'CLOSEPAREN':
        raise ParseError(
            "Found \")\" without a corresponding \"(\"",
            first_token.line_no,
            first_token.char_no,
        )
    elif first_token.type == 'CLOSEBRACKET':
        raise ParseError(
            "Found \"]\" without a corresponding \"[\"",
            first_token.line_no,
            first_token.char_no,
        )
    elif first_token.type == 'CLOSEANGLEBRACKET':
        raise ParseError(
            "Found \">\" without a corresponding \"<\"",
            first_token.line_no,
            first_token.char_no,
        )
    elif first_token.type in ('OPENBRACE', 'CLOSEBRACE'):
        raise ParseError(
            "Blocks (\"{\" or \"}\") can't be used where a number or variable is expected. Did you possibly misspell a Repeat or Question at the start of the line?",
            first_token.line_no,
            first_token.char_no,
        )
    else:
        raise ParseError(
            "Cannot use command \"%s\" where a number or variable is expected" % (
                first_token.value,
            ),
            first_token.line_no,
            first_token.char_no,
        )

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
        '/' : (1, 'LEFT'),
        '%' : (1, 'LEFT')
    }

    # grab the open paren token
    open_paren_token = pop_asserting_present(tokens)

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
            raise ParseError(
                'Math operator "%s" needs values on both sides' % op_token.value,
                op_token.line_no,
                op_token.char_no,
            )

        node_tokens = left.tokens + [op_token] + right.tokens
        new_node = DBNBinaryOpNode(
            value=op_token.value,
            children=[left, right],
            tokens=node_tokens,
        )
        output_stack.append(new_node)

    parsing = True
    while parsing:
        first_token = peek_asserting_present(tokens)

        if  first_token.type == 'CLOSEPAREN':
            parsing = False
            close_paren_token = pop_asserting_present(tokens)

        elif first_token.type == 'OPERATOR':
            op_token = pop_asserting_present(tokens)
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

    # so now the root op node should be the one element left in the list
    # if there isn't eactly one thing left, it's an error

    if len(output_stack) > 1:
        raise ParseError(
            "Missing math operator inside parentheses",
            open_paren_token.line_no,
            open_paren_token.char_no,
        )

    if not output_stack:
        raise ParseError(
            "Empty parentheses",
            open_paren_token.line_no,
            open_paren_token.char_no,
        )

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
    open_bracket_token = pop_asserting_present(tokens)

    if peek_asserting_present(tokens).type == 'CLOSEBRACKET':
        raise ParseError(
            "There must be two arguments within the brackets to describe a dot, got none",
            open_bracket_token.line_no,
            open_bracket_token.char_no,
        )
    first_arg = parse_arg(tokens)

    if peek_asserting_present(tokens).type == 'CLOSEBRACKET':
        raise ParseError(
            "There must be two arguments within the brackets to describe a dot, got only one",
            open_bracket_token.line_no,
            open_bracket_token.char_no,
        )
    second_arg = parse_arg(tokens)


    next_token = peek_asserting_present(tokens)
    if next_token.type != 'CLOSEBRACKET':
        raise ParseError(
            "There must be two arguments within the brackets to describe a dot, got extra (\"%s\")" % (next_token.value),
            next_token.line_no,
            next_token.char_no,
        )
    close_bracket_token = tokens.pop(0)

    node_tokens = [open_bracket_token] + first_arg.tokens + second_arg.tokens + [close_bracket_token]
    return DBNBracketNode(
        children=[first_arg, second_arg],
        tokens=node_tokens,
    )

def parse_number_call(tokens):
    """
    < name ... >
    """
    open_angle_bracket_token = pop_asserting_present(tokens)

    next_token = peek_asserting_present(tokens)
    if next_token.type != 'WORD':
        raise ParseError(
            "To call a number, the name of the Number must be the first thing after the \"<\", got \"%s\"" % next_token.value,
            next_token.line_no,
            next_token.char_no
        )
    number_name = parse_word(tokens)

    args = []
    parsing_args = True
    while parsing_args:
        first_token = peek_asserting_present(tokens)

        if first_token.type == 'CLOSEANGLEBRACKET':
            parsing_args = False
            close_angle_bracket_token = pop_asserting_present(tokens)
        else:
            args.append(parse_arg(tokens))

    node_tokens = [open_angle_bracket_token] + number_name.tokens
    for arg in args:
        node_tokens.extend(arg.tokens)
    node_tokens += [close_angle_bracket_token]

    return DBNProcedureCallNode(
        value='number',
        children=[number_name] + args,
        tokens=node_tokens,
    )

def parse_word(tokens):
    """
    token is just one token
    """
    word_token = tokens.pop(0)
    if not word_token.type == 'WORD':
        raise AssertionError("parse_word called but first token on stack is not a word (its a %s)" % word_token.type)
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
        raise AssertionError("parse_number called but first token on stack is not a number (its a %s)" % number_token.type)
    return DBNNumberNode(
        value=number_token.value,
        tokens=[number_token],
    )

def peek_asserting_present(tokens):
    if not tokens:
        raise AssertionError("expected there to be tokens, but none found")
    return tokens[0]

def pop_asserting_present(tokens):
    if not tokens:
        raise AssertionError("expected there to be tokens, but none found")
    return tokens.pop(0)

def validate_not_newline(token, message):
    if token.type == 'NEWLINE':
        raise ParseError(message, token.line_no, token.char_no)

def validate_is_newline(token, message):
    if token.type != 'NEWLINE':
        raise ParseError(message, token.line_no, token.char_no)


def format_block_owning_token_name(block_owning_token):
    if block_owning_token.type == 'QUESTION':
        return 'Question body'
    elif block_owning_token.type == 'REPEAT':
        return 'Repeat body'
    elif block_owning_token.type == 'COMMAND' or block_owning_token.type == 'NUMBERDEF':
        return '%s definition body' % (block_owning_token.value)
    else:
        return 'block'

def raise_unexpected_block_start_end_of_input(block_owning_token):
    if block_owning_token:
        raise ParseError(
            "Unexpected end of input looking for opening \"{\" of %s" % (
                format_block_owning_token_name(block_owning_token),
            ),
            block_owning_token.line_no,
            block_owning_token.char_no
        )
    else:
        raise AssertionError("end of input reached but no owning block token")

def raise_unexpected_block_end_end_of_input(block_owning_token):
    if block_owning_token:
        raise ParseError(
            "Unexpected end of input looking for closing \"}\" of %s" % (
                format_block_owning_token_name(block_owning_token),
            ),
            block_owning_token.line_no,
            block_owning_token.char_no,
        )
    else:
        raise AssertionError("end of input reached looking for closing } but no owning block token")

def raise_unexpected_block_opening_token(block_owning_token, unexpected_token):
    if block_owning_token:
        raise ParseError(
            "%s needs to start with \"{\", got \"%s\"" % (
                format_block_owning_token_name(block_owning_token),
                unexpected_token.value,
            ),
            unexpected_token.line_no,
            unexpected_token.char_no,
        )
    else:
        raise AssertionError("no block_owning_token but bad delimiter start: %s" % unexpected_token.value)
