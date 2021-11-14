"""
defines the builtin functions
"""

from .structures import BuiltinProcedure, LinkedFunctions
from . import opcodes

def builtin(procedure_type, nargs):
    def decorator(fn):
        return BuiltinProcedure(fn.__name__, procedure_type, nargs, fn)
    return decorator


@builtin('command', 4)
def Line(compiler, node):
    label = compiler.generate_label("postLineCall")
    compiler.emit_push_label(label)
    compiler.update_stack(1, 'Line Return')

    # get the arguments on the stack in the weird order Line expects:
    # [y1|x1|y0|x0
    compiler.visit(node.args[0])
    compiler.visit(node.args[1])
    compiler.visit(node.args[2])
    compiler.visit(node.args[3])

    # run the command!
    compiler.emit_linked_function_jump(LinkedFunctions.LINE_COMMAND)
    compiler.emit_label(label)

    compiler.update_stack(-5, 'Line')


@builtin('command', 1)
def Pen(compiler, node):
    compiler.visit(node.args[0])
    compiler.emit_raw("MSTORE(%d, $$)" % compiler.PEN_ADDRESS)

    compiler.update_stack(-1, 'Pen')


@builtin('command', 1)
def Paper(compiler, node):
    label = compiler.generate_label("postPaperCall")
    compiler.emit_push_label(label)
    compiler.update_stack(1, 'Paper Internal return')

    compiler.visit(node.args[0])

    # run the command!
    compiler.emit_linked_function_jump(LinkedFunctions.PAPER_COMMAND)
    compiler.emit_label(label)

    compiler.update_stack(-2, 'Paper')


@builtin('command', 5)
def Field(compiler, node):
    label = compiler.generate_label("postFieldCall")
    compiler.emit_push_label(label)
    compiler.update_stack(1, 'Field Return')

    for arg in reversed(node.args):
        compiler.visit(arg)

    compiler.emit_linked_function_jump(LinkedFunctions.FIELD_COMMAND)
    compiler.emit_label(label)

    compiler.update_stack(-6, 'Field')


@builtin('number', 1)
def Time(compiler, node):
    label = compiler.generate_label("postTimeCall")
    compiler.emit_push_label(label)
    compiler.update_stack(1, 'Time Internal return')

    compiler.visit(node.args[0])

    compiler.emit_linked_function_jump(LinkedFunctions.TIME_NUMBER)
    compiler.emit_label(label)

    compiler.update_stack(-1, 'Time (leaving return value on stack)')


@builtin('number', 0)
def Address(compiler, node):
    compiler.emit_opcode(opcodes.ADDRESS)
    compiler.update_stack(1, 'Address left on stack')


@builtin('number', -1)
def Call(compiler, node):
    # this needs to do its own argument count validation
    # args are: [address method args*]
    # where we can have up to 6 args
    # (we have 8 scratch words, and need 1 for return,
    # and the method descriptor takes 1)
    if len(node.args) < 2:
        raise CompileError(
            "'Call' number requires at least two params: the address and method",
            compiler.line_no
        )  

    if len(node.args) > (2 + 6):
        raise CompileError(
            "'Call' can take at most six numbers in addition to the address and method",
            compiler.line_no,
        )

    # Ok — so stack to call are:
    # [method|nargs|args*|address|ret
    # input is:
    # [address, method, args*]
    label = compiler.generate_label('postCallCall')
    compiler.emit_push_label(label)
    compiler.update_stack(1, 'Call Call internal return')
    compiler.visit(node.args[0])

    for arg in reversed(node.args[2:]):
        compiler.visit(arg)

    compiler.emit_push(len(node.args) - 2)
    compiler.update_stack(1, 'Call Call nargs')

    compiler.visit(node.args[1])

    compiler.emit_linked_function_jump(LinkedFunctions.CALL_NUMBER)
    compiler.emit_label(label)

    compiler.update_stack(-1*(len(node.args) + 1), 'Call Call nargs')  
