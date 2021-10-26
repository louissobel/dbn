import sys
import contextlib

from . import structures
from parser.structures.ast_nodes import *
from parser import DBNAstVisitor

from .symbol_collector import SymbolCollector
from .opcodes import *

def compile(node, *args, **kwargs):
    compiler = DBNEVMCompiler()
    return compiler.compile(node, *args, **kwargs)


class DBNEVMCompiler(DBNAstVisitor):

    """
    Memory layout
    0x0000 : right-aligned 20byte owning contract address
    0x0020 : boolean byte indicating that the bitmap is fully initialized
    0x0021 : []
    0x0040 : Pen
    0x0060 : Env pointer
    0x0080 : [bitmap starts...]
    .... (bitmap is 40 + 14 + 404 + 101*104 = 10962 long)
    0x2B60 : Env start
    """
    BITMAP_BASE = 0x80
    PIXEL_DATA_START = BITMAP_BASE + 14 + 40 + 404
    PEN_ADDRESS = 0x40

    ENV_POINTER_ADDRESS = 0x60
    FIRST_ENV_ADDRESS = 0x2B60

    """
    Env layout:
    0x00 : 256 bit bitmap of "variable present"
    0x20 : parent env pointer
    0x40 : beginning of env values
    ...

    """

    # other constants
    INITIAL_PEN_VALUE = 100
    BUILTIN_COMMANDS = {'Line', 'Pen', 'Paper'}

    def __init__(self, verbose=False):
        self.verbose = verbose

    def generate_label(self, prefix):
        """
        generates a unique label for given prefix
        """
        count = self.label_prefix_counts.get(prefix, 0)
        label_name = "dbnDrawCompiled0%s%d" % (prefix, count)
        self.label_prefix_counts[prefix] = count + 1
        return label_name

    def log(self, message):
        prefix = ''
        if self.getting_block_dependencies:
            prefix = '>>>> Getting Block Dependencies: '
        if self.verbose:
            print(prefix + str(message), file=sys.stderr)

    def compile(self, node, metadata=structures.EMPTY_METADATA):
        self.lines = []
        self.label_prefix_counts = {}
        self.line_no = 0

        # stack_size is relative to command / program scope
        self.stack_size = 0
        self.getting_block_dependencies = False

        symbol_collector = SymbolCollector().collect_symbols(node)
        self.symbol_mapping = dict(
            (s, i) for i, s in enumerate(symbol_collector.variables)
        )
        self.log(self.symbol_mapping)

        # Initially, we _know_ all variables are local.
        # if we are not in a command then they all default to present
        self.symbol_directory = structures.SymbolDirectory().with_locals(
            symbol_collector.variables
        )

        self.procedure_definitions_by_name = {
            dfn.name : dfn for dfn in symbol_collector.procedure_definitions
        }
        for dfn in symbol_collector.procedure_definitions:
            dfn.block_dependencies = self.get_procedure_block_dependencies(dfn.node)
            self.log(dfn.block_dependencies)

        self.log(self.procedure_definitions_by_name)

        self.visit(node)

        # Special metadata functions
        self.emit_metadata(metadata)

        return "\n".join(self.lines)

    @contextlib.contextmanager
    def new_symbol_directory(self, new_directory, why='unknown'):
        old_directory = self.symbol_directory
        self.symbol_directory = new_directory
        self.log("Pushing new directory (%s): %s" % (why, self.symbol_directory))
        yield
        self.symbol_directory = old_directory

    @contextlib.contextmanager
    def stashed_state_to_get_block_dependencies(self):
        old_lines = self.lines
        self.lines = []

        old_label_prefix_counts = self.label_prefix_counts
        self.label_prefix_counts = {}

        self.getting_block_dependencies = True
        self.block_dependencies = structures.BlockDependencies()
        yield
        self.block_dependencies = None
        self.getting_block_dependencies = False

        self.label_prefix_counts = old_label_prefix_counts

        self.lines = old_lines

    def emit_comment(self, comment):
        # TODO: escape the comment?
        self.lines.append("; %s" % comment)

    def emit_debug(self):
        label = self.generate_label("debug")

        # TODO: add some kind of option to make this throw
        self.emit_raw("@%s [0xdd]" % label)

    def emit_newline(self):
        self.lines.append("")

    def emit_opcode(self, opcode):
        self.lines.append(opcode.ethasm_format())
        return self

    def emit_push(self, literal):
        # TODO: format the literal as hex?
        self.lines.append(str(literal))
        return self

    def emit_push_label(self, label):
        self.lines.append("$%s" % label)
        return self

    def emit_label(self, label):
        self.lines.append("@%s:" % label)

    def emit_jump(self, label):
        self.lines.append("JUMP($%s)" % label)
        return self

    def emit_jumpi(self, label):
        self.lines.append("JUMPI($%s, $$)" % label)
        return self

    def emit_bit_for_index(self, index):
        """
        gets 1 << index onto the stack
        chooses between:
         - index in [0, 7]:   PUSH1(1 << index) (2 bytes)
         - index in [8, 15]:  PUSH2(1 << index) (3 bytes)
         - index in [16, 23]: PUSH3(1 << index) (4 bytes)
         - else:              SHL(index, 1):   (PUSH1(1), PUSH1(index), SHL) (5 bytes)
        """
        if index > 255:
            raise ValueError("index mustn't be greater than 255!! too many variables?")

        if index <= 23:
            self.emit_push(1 << index)
        else:
            # TODO: need to make sure I cover this in a test, it means a lot of variables!
            self.emit_raw("SHL(%d, 1)" % index)
        return self

    def emit_load_env_base(self):
        self.emit_raw("MLOAD(%d)" % self.ENV_POINTER_ADDRESS)
        return self

    def emit_line_no(self, line_no):
        # just comment for now
        # TODO: debug mode where we spit this out for real?
        self.log("-- Line Number %d" % line_no)
        self.emit_newline()
        self.emit_comment("line number: %d" % line_no)
        self.line_no = line_no
        return self

    def emit_raw(self, data):
        self.lines.append(data)


    def emit_metadata(self, metadata):

        # owningContract
        if metadata.owning_contract:
            self.validate_metadata_hex_string('owning_contract', metadata.owning_contract, expected_length=20)
            # TODO: verify it's a 20 byte hex string?
            self.emit_raw("@metadataOwningContract [!%s]" % metadata.owning_contract)
        else:
            self.emit_raw("@metadataOwningContract []")

        # description
        if metadata.description:
            self.validate_metadata_hex_string('description', metadata.description)
            self.emit_raw("@metadataDescription [!%s]" % metadata.description)
        else:
            self.emit_raw("@metadataDescription []")

    def validate_metadata_hex_string(self, name, s, expected_length=None):
        if not s[0:2] == '0x':
            raise ValueError('metadata %s (%s) is not hex string' % (name, s))

        if len(s) == 2:
            raise ValueError('metadata %s (%s) is empty hex string!' % (name, s))

        if len(s) % 2 == 1:
            raise ValueError('metadata %s (%s) is odd length!' % (name, s))

        if expected_length:
            if (len(s) - 2)/2 != expected_length:
                raise ValueError('metadata %s (%s) is unexpected length! (wanted %d)' % (name, s, expected_length))


    ###
    # Stack tracking
    def update_stack(self, n, why='unknown'):
        self.log("Updating stack (%s): %d --> %d" % (
            why,
            self.stack_size,
            self.stack_size + n,
        ))
        self.stack_size += n

    @contextlib.contextmanager
    def fresh_stack(self, why='unknown'):
        self.log("Pushing fresh stack (%s): 0" % why)
        old_stack_size = self.stack_size
        self.stack_size = 0
        yield
        self.stack_size = old_stack_size

    ####
    # Visitor methods

    def visit_program_node(self, node):
        self.emit_comment(";;;;;;; DBN Drawing!")
        self.emit_newline()

        self.emit_label('dbnDraw')

        self.emit_comment("initialize pen to %d" % self.INITIAL_PEN_VALUE)
        self.emit_raw("MSTORE(%d, %d)" % (self.PEN_ADDRESS, self.INITIAL_PEN_VALUE))

        self.emit_comment("initialize base environment at %d" % self.FIRST_ENV_ADDRESS)
        # save the first env address to the env pointer
        self.emit_raw("MSTORE(%d, %d)" % (self.ENV_POINTER_ADDRESS, self.FIRST_ENV_ADDRESS))
        # initialization is just setting the bitmap to 0xFF...FF
        self.emit_raw("MSTORE(%d, NOT(0))" % self.FIRST_ENV_ADDRESS)

        # TODO: Emit some comments about the memory layout?

        self.visit_block_node(node)

        self.emit_newline()
        self.emit_comment("return to caller control")
        self.emit_jump("dbnDrawComplete")
        self.emit_comment(";;;;;;; End DBN Drawing")
        self.emit_newline()
        self.emit_opcode(STOP)
        self.emit_newline()

    def visit_block_node(self, node):
        # save for internal assertions to check stack accounting
        stack_size_entering = self.stack_size

        symbol_directory_for_this_block = self.symbol_directory.copy()
        with self.new_symbol_directory(symbol_directory_for_this_block, 'block'):
            for sub_node in node.children:
                self.visit(sub_node)

                # If we set a variable in a block, for the remainder of the block
                # we can later assume that that variable is present
                # (and use optimized read path)
                if self.is_variable_set(sub_node):
                    symbol = sub_node.left.value
                    if symbol_directory_for_this_block.location_for(symbol).is_global():
                        symbol_directory_for_this_block.set_local(symbol)
                        self.log("Update directory for set (%s) in block: %s" % (symbol, self.symbol_directory))

        # some internal assertions to check stack accounting
        if self.stack_size != stack_size_entering:
            raise RuntimeError("unbalanced stack for block! %d entering, %d after" % (
                stack_size_entering,
                self.stack_size,
            ))

    def is_variable_set(self, node):
        return isinstance(node, DBNSetNode) and isinstance(node.left, DBNWordNode)

    def visit_set_node(self, node):
        self.emit_line_no(node.line_no)

        left = node.left

        # If left is a bracket, we're setting a single dot
        if   isinstance(left, DBNBracketNode):
            # Peer inside the bracket
            bracket_left, bracket_right = left.children

            label = self.generate_label("postSetCommand")
            self.emit_push_label(label) # return
            self.update_stack(1, "Set command internal")

            self.visit(node.right)      # color
            self.visit(bracket_left)    # x
            self.emit_push(self.PIXEL_DATA_START)
            self.visit(bracket_right)   # y
            self.emit_jump('setCommand')
            self.emit_label(label)

            self.update_stack(-4, 'set dot')

        elif isinstance(left, DBNWordNode):
            # Get the value on the stack
            self.visit(node.right)

            # If we already know the symbol is local,
            # then we don't need  to flip the bitmap.
            # but regardless, all sets are "local" for purposes
            # of tracking dependencies
            symbol = left.value

            if self.getting_block_dependencies:
                self.block_dependencies.variable_sets.append(
                    structures.BlockDependencies.VariableAccess(
                        symbol,
                        self.stack_size,
                        False,
                        self.line_no,
                    )
                )

            location = self.symbol_directory.location_for(symbol)
            self.log("SET %s (%s), stack_size: %d, directory: %s" % (symbol, location, self.stack_size, self.symbol_directory))
            self.emit_comment('   -> setting %s' % symbol)
            if location.is_local():
                self.handle_env_set_local(symbol)
            elif location.is_stack():
                # [value|...
                distance = self.stack_size - location.slot - 1 # (-1 to account for value at top)
                if distance > 16:
                    raise AssertionError("cannot set stack-stored symbol! too deep!")
                if distance < 1:
                    raise AssertionError("cannot set stack-stored symbol! distance somehow < 1...")

                opcode = [
                    SWAP1,
                    SWAP2,
                    SWAP3,
                    SWAP4,
                    SWAP5,
                    SWAP6,
                    SWAP7,
                    SWAP8,
                    SWAP9,
                    SWAP10,
                    SWAP11,
                    SWAP12,
                    SWAP13,
                    SWAP14,
                    SWAP15,
                    SWAP16,
                ][distance-1]
                self.emit_opcode(opcode)
                self.emit_opcode(POP)

            else:
                self.handle_env_set(symbol)

            self.update_stack(-1, 'set variable')

    def visit_word_node(self, node):
        symbol = node.value

        location = self.symbol_directory.location_for(symbol)

        if self.getting_block_dependencies:
            self.block_dependencies.variable_gets.append(
                structures.BlockDependencies.VariableAccess(
                    symbol,
                    self.stack_size,
                    location.is_global(),
                    self.line_no,
                )
            )

        self.log("GET %s (%s), stack_size: %d, directory: %s" % (symbol, location, self.stack_size, self.symbol_directory))
        self.emit_comment('   -> getting %s' % symbol)
        if location.is_local():
            self.handle_env_get_local(symbol)
        elif location.is_stack():
            distance = self.stack_size - location.slot
            if distance > 16:
                raise AssertionError("cannot access stack-stored symbol! too deep!")
            if distance < 1:
                raise AssertionError("cannot access stack-stored symbol! distance somehow < 1...")

            opcode = [
                DUP1,
                DUP2,
                DUP3,
                DUP4,
                DUP5,
                DUP6,
                DUP7,
                DUP8,
                DUP9,
                DUP10,
                DUP11,
                DUP12,
                DUP13,
                DUP14,
                DUP15,
                DUP16,
            ][distance-1]
            self.emit_opcode(opcode)
        else:
            self.handle_env_get(symbol)

        self.update_stack(1, 'get variable')

    def handle_env_set_local(self, symbol):
        """
        assumes value to set is top of stack
        _and_ that the bitmap is already set for
        this symbol
        """

        # TODO: better error message for unexpected symbol
        index = self.symbol_mapping[symbol]

        self.emit_load_env_base()  # [env_base|value
        self.emit_raw("ADD(%d, $$)" % ((2 + index) * 32)) # [addr|value
        self.emit_opcode(MSTORE)

    def handle_env_set(self, symbol):
        """
        assumes value to set is top of stack
        """

        # TODO: better error message for unexpected symbol
        index = self.symbol_mapping[symbol]

        self.emit_load_env_base()       # [env_base

        # toggle bitmap
        self.emit_opcode(DUP1)          # [env_base|env_base
        self.emit_opcode(MLOAD)         # [bitmap|env_base
        self.emit_bit_for_index(index)  # [bit|bitmap|env_base
        self.emit_opcode(OR)            # [new_bitmap|env_base
        self.emit_opcode(DUP2)          # [env_base|new_bitmap|env_base
        self.emit_opcode(MSTORE)        # [env_base

        # address is env_base + (2 + index)*32
        self.emit_raw("ADD(%d, $$)" % ((2 + index) * 32))
        self.emit_raw("MSTORE($$, $$)")


    def handle_env_get_local(self, symbol):
        """
        Optimization for formal args, repeat args, etc
        where we don't need to check the bitmap / climb the env
        """
        # TODO: better error message for unexpected symbol
        index = self.symbol_mapping[symbol]

        self.emit_load_env_base()
        self.emit_raw("ADD(%d, $$)" % ((2 + index) * 32))
        self.emit_raw("MLOAD($$)")

    def handle_env_get(self, symbol):
        """
        call helper function, which takes args
        [env_base|bit|wordoffset
        """
        # TODO: better error message for unexpected symbol
        index = self.symbol_mapping[symbol]
        label = self.generate_label("afterEnvGetCall")

        self.emit_push_label(label)       # return
        self.emit_push((2 + index) * 32)  # wordoffset
        self.emit_bit_for_index(index)    # bit
        self.emit_load_env_base()         # env_base
        self.emit_jump('envGet')
        self.emit_label(label)


    def visit_repeat_node(self, node):
        self.emit_line_no(node.line_no)

        # Set the bitmap for the loop var
        var_symbol = node.var.value
        location = self.symbol_directory.location_for(var_symbol)
        if not location.is_local():
            # then I need to set the bitmap..
            # TODO: better error message?
            index = self.symbol_mapping[var_symbol]

            # also the layering here feels kind of messy...

            self.emit_load_env_base()       # [env_base

            # toggle bitmap
            self.emit_opcode(DUP1)          # [env_base|env_base
            self.emit_opcode(MLOAD)         # [bitmap|env_base
            self.emit_bit_for_index(index)  # [bit|bitmap|env_base
            self.emit_opcode(OR)            # [new_bitmap|env_base
            self.emit_opcode(SWAP1)         # [env_base|new_bitmap
            self.emit_opcode(MSTORE)        # [

        self.visit(node.end)
        self.visit(node.start)

        # [start|end

        ## figure out the step
        # assume it's 1
        self.emit_push(1) # [1|start|end
        # and if end > start, we're correct!
        self.emit_opcode(DUP2) # [start|1|start|end
        self.emit_opcode(DUP4) # [end|start|1|start|end
        self.emit_opcode(SGT) # [end>start|1|start|end

        body_entry_label = self.generate_label("repeatBodyEntry")

        self.emit_jumpi(body_entry_label)
        # but if end <= start, flip it to -1
        self.emit_raw("SUB(0, $$)")

        ##### loop entry
        # [step|value|end
        self.emit_label(body_entry_label)

        # set value in the environment
        self.emit_opcode(DUP2)

        # For dependency tracking purposes, this is a regular set
        # (that just happens to have the bitmap set elsewhere)
        # TOOD: reeaeeally not sure about this
        if self.getting_block_dependencies:
            self.block_dependencies.variable_sets.append(
                structures.BlockDependencies.VariableAccess(
                    var_symbol,
                    self.stack_size,
                    False,
                    self.line_no,
                )
            )
        self.handle_env_set_local(var_symbol)

        # and then the body itself!
        # while we visit it, we _know_ the var is set
        self.update_stack(1, 'repeat body')
        with self.new_symbol_directory(self.symbol_directory.with_local(node.var.value), 'repeat'):
            self.visit(node.body)

        # and now loop!
        # stack will still be
        # [step|value|end
        # if value == end, exit
        self.emit_opcode(DUP2) # [value|step|value|end
        self.emit_opcode(DUP4) # [end|value|step|value|end
        self.emit_opcode(EQ) # [end=value|step|value|end

        loop_end = self.generate_label("repeatDone")
        self.emit_jumpi(loop_end)

        # but otherwise, increment (or decrement) and loop!
        # [step|value|end
        self.emit_opcode(DUP1) # [step|step|value|end
        self.emit_opcode(SWAP2) # [value|step|step|end
        self.emit_opcode(ADD) # [value+step|step|end
        self.emit_opcode(SWAP1) # [step|value+step|end
        self.emit_jump(body_entry_label)


        self.emit_label(loop_end)
        # clean up stack
        self.emit_opcode(POP)
        self.emit_opcode(POP)
        self.emit_opcode(POP)

        self.update_stack(-3, 'repeat end')

    def visit_question_node(self, node):
        self.emit_line_no(node.line_no)

        self.visit(node.right)
        self.visit(node.left)

        # map to comparison and "flip" if we flip the JUMPI input
        questions = {
            # Same --> jump around if not same
            'Same': (EQ, True),

            # NotSame --> jump around if same
            'NotSame': (EQ, False),

            # Smaller --> jump around if not smaller
            'Smaller': (SLT, True),

            # Smaller --> jump around if smaller
            'NotSmaller': (SLT, False),
        }

        compare_op, should_flip = questions[node.value]
        self.emit_opcode(compare_op)
        if should_flip:
            self.emit_raw("XOR(1, $$)")

        after_body_label = self.generate_label('questionAfterBody')
        self.emit_jumpi(after_body_label)

        self.update_stack(-2, 'question')
        self.visit(node.body)
        self.emit_label(after_body_label)

    def visit_procedure_call_node(self, node):
        if node.procedure_type == 'command':
            self.emit_line_no(node.line_no)
        else:
            # TODO: handle numbers
            raise ValueError("can only handle commands right now!")

        procedure_name = node.procedure_name.value
        if procedure_name == "Line":
            self.handle_builtin_line(node)
        elif procedure_name == "Pen":
            self.handle_builtin_pen(node)
        elif procedure_name == "Paper":
            self.handle_builtin_paper(node)
        elif procedure_name == "DEBUGGER":
            self.emit_debug()
        else:
            if self.getting_block_dependencies:
                self.block_dependencies.procedures_called.append(
                    structures.BlockDependencies.VariableAccess(
                        procedure_name,
                        self.stack_size,
                        True,
                        self.line_no,
                    )
                )

            """
            Ok: calling discipline
            Caller:
             - pushes return address on the stack
             - mints a fresh environment
                - bitmap is zero
                - parent is set
             - sets up the stack vars
             - copies local vars ito the new environment
            Callee:
             - promises to pop any stack vars
             - promises to jump back to return address!
            Caller:
             - pops away the environment

            """
            # TODO: better error messages!!
            try:
                dfn = self.procedure_definitions_by_name[procedure_name]
            except KeyError:
                raise ValueError("no definition for %s" % procedure_name)

            if dfn.label is None:
                raise ValueError("%s not yet defined" % procedure_name)

            if len(node.args) != len(dfn.args):
                # TODO: line numbers!
                raise ValueError("%s expects %d args, got %d" % (
                    procedure_name,
                    len(dfn.args),
                    len(node.args),
                ))

            post_call_label = self.generate_label('postUserProcedureCall')

            # Return value
            self.emit_push_label(post_call_label)
            self.update_stack(1, 'Command Return Destination')

            arg_nodes_by_name = dict(zip(dfn.args, node.args))
            # First, stack args (reversed)
            self.log("PROC CALL found stack args: %s" % dfn.stack_args)
            for arg in reversed(dfn.stack_args):
                self.visit(arg_nodes_by_name[arg])

            # Then, local env args (also reversed)
            for arg in reversed(dfn.local_env_args):
                self.visit(arg_nodes_by_name[arg])

            # Ok, initialize new environment

            # Load current ENV_BASE.
            self.emit_load_env_base()                              # [old_env_base
            self.emit_opcode(DUP1)                                 # [old_env_base|old_env_base 
            next_env_increment = (2 + len(self.symbol_mapping)) * 32
            self.emit_raw("ADD(%d, $$)" % next_env_increment)      # [new_env_base|old_env_base

            # We need to
            #  a) store old_env_base in new_env_base+32 (parent pointer)
            #  b) save the new env base _back_ to the ENV_POINTER_ADDRESS
            #  c) initialize new_env_base to the new bitmap
            #  d) save the new variables in the env
            self.emit_opcode(SWAP1)     # [old_env_base|new_env_base
            self.emit_opcode(DUP2)      # [new_env_base|old_env_base|new_env_base
            self.emit_raw("ADD(32, $$)")# [new_env_base+32|old_env_base|new_env_base
            self.emit_opcode(MSTORE)    # [new_env_base

            self.emit_opcode(DUP1)      # [new_env_base|new_env_base
            self.emit_raw("MSTORE(%d, $$)" % self.ENV_POINTER_ADDRESS) # [new_env_base

            # build the bitmap
            if not dfn.local_env_args:
                self.emit_push(0)           # [0|new_env_base
            else:
                for i, symbol in enumerate(dfn.local_env_args):
                    index = self.symbol_mapping[symbol] # TODO: better error message?
                    self.emit_bit_for_index(index)

                    if i != 0:
                        self.emit_opcode(OR)

            self.emit_opcode(DUP2)     # [new_env_base|new_bitmap|new_env_base
            self.emit_opcode(MSTORE)   # [new_env_base

            # Store the arguments!
            # Currently on the stack with the top being the first, etc
            # We don't use the same code as "Set" handling because we
            # already have the bitmap set and the env_base on the stack
            for symbol in dfn.local_env_args:                       # [new_env_base|arg*
                index = self.symbol_mapping[symbol] # TODO: better error message?
                self.emit_opcode(SWAP1)                             # [arg*|new_env_base
                self.emit_opcode(DUP2)                              # [new_env_base|arg*|new_env_base
                self.emit_raw("ADD(%d, $$)" % ((2 + index) * 32))   # [env_location|arg*|new_env_base
                self.emit_raw("MSTORE($$, $$)")                     # [new_env_base|arg*
            self.emit_opcode(POP)                                   # [

            self.emit_jump(dfn.label)
            self.emit_label(post_call_label)

            # Post Call:
            #  - reset current env to the parent env
            self.emit_load_env_base()
            self.emit_raw("ADD(32, $$)")
            self.emit_opcode(MLOAD)
            self.emit_raw("MSTORE(%d, $$)" % self.ENV_POINTER_ADDRESS)

            self.update_stack(-1 * (len(dfn.args) + 1), 'Command call')

    def handle_builtin_pen(self, node):
        if len(node.args) != 1:
            raise self.invalid_argument_count("Pen", 1, len(node.args))

        self.emit_comment("set Pen")
        self.visit(node.args[0])
        self.emit_raw("MSTORE(%d, $$)" % self.PEN_ADDRESS)

        self.update_stack(-1, 'Pen')

    def handle_builtin_line(self, node):
        # first, return address
        label = self.generate_label("postLineCall")

        self.emit_push_label(label)
        self.emit_push(self.PIXEL_DATA_START)
        self.emit_raw("MLOAD(%d) ; get pen" % self.PEN_ADDRESS)

        self.update_stack(3, 'Line Internals')

        if len(node.args) != 4:
            raise self.invalid_argument_count("Line", 4, len(node.args))

        # get the arguments on the stack in reverse order
        for arg_node in reversed(node.args):
            self.visit(arg_node)

        # run the command!
        self.emit_jump('lineCommand')
        self.emit_label(label)

        self.update_stack(-7, 'Line')

    def handle_builtin_paper(self, node):
        label = self.generate_label("postPaperCall")

        self.emit_push_label(label)
        self.emit_push(self.PIXEL_DATA_START)
        self.update_stack(2, 'Paper Internals')

        if len(node.args) != 1:
            raise self.invalid_argument_count("Paper", 1, len(node.args))

        self.visit(node.args[0])

        # run the command!
        self.emit_jump('paperCommand')
        self.emit_label(label)

        self.update_stack(-3, 'Paper')

    def invalid_argument_count(self, command_name, expected, got):
        return ValueError("%s expects %d arguments, got %d" % (command_name, expected, got))

    def visit_procedure_definition_node(self, node):
        self.emit_line_no(node.line_no)

        dfn = self.procedure_definitions_by_name[node.procedure_name.value]
        procedure_start_label = self.generate_label('userProcedureDefinition')
        dfn.label = procedure_start_label

        after_procedure_label = self.generate_label('afterUserProcedureDefinition')

        # Move execution to after the procedure body
        self.emit_jump(after_procedure_label)

        self.emit_label(procedure_start_label)

        # we also track stack from zero...
        with self.fresh_stack('command_def'):

            local_env_args = []

            # list built in order of the sack, as in
            # [a, b, c], the stack should end up [a|b|c
            # (and we  need to assign stack location in reverse)
            # this is so that we can understand depth by a simple
            # increment rather than re-computing the whole get / set list
            stack_args = []

            if dfn.block_dependencies:
                # Then let's try and figure out what can go on the stack!
                self.log("\n\n[][][][][][][] Stack decision for %s" % dfn.name)

                for arg in dfn.args:
                    stack_eligible = dfn.block_dependencies.is_stack_eligible(
                        arg,
                        self.procedure_definitions_by_name,
                        # for checking eligbility, we shift the stack by the number of
                        # stack_args that we've already decided to allocate
                        # TODO: should we optimize the order in some way?
                        shift_stack=len(stack_args),
                    )

                    if stack_eligible:
                        stack_args.append(arg)
                    else:
                        local_env_args.append(arg)

                self.log("local: %s" % local_env_args)
                self.log("stack: %s" % stack_args)
                self.log("[][][][][][][]\n\n")
            else:
                local_env_args = dfn.args

            # While we're visiting the body, we _know_
            # that the formal args will always be set
            new_directory = (structures.SymbolDirectory()
                .with_locals(local_env_args)
                .with_stack({s: i for (i, s) in enumerate(reversed(stack_args))})
            )

            # Callee will take care of making sure these are in place
            dfn.stack_args = stack_args
            self.log("setting stack args: %s" % stack_args)
            dfn.local_env_args = local_env_args

            self.update_stack(len(dfn.stack_args), 'procedure stack args')

            with self.new_symbol_directory(new_directory, 'command_def'):
                self.visit(node.body)

            # But _we_ are responsible for popping the stack variables away
            # (before jump)
            for _ in range(len(dfn.stack_args)):
                self.emit_opcode(POP)
            self.update_stack(-1 * len(dfn.stack_args), 'procedure stack args pop')

        # TODO: emit default return value if it is a Number?
        # self.add('LOAD_INTEGER', 0)
        self.emit_raw('JUMP($$)')

        self.emit_label(after_procedure_label)

    def visit_value_node(self, node):
        # TODO!
        self.emit_line_no(node.line_no)
        self.visit(node.result)
        self.add('RETURN')

    def visit_load_node(self, node):
        # TODO!
        self.emit_line_no(node.line_no)
        self.add('LOAD_CODE', node.value)

    def visit_bracket_node(self, node):
        # get the stack to be
        # [y|x
        self.visit(node.left)
        self.visit(node.right)

        # Y*104 + X is the byte
        self.emit_raw("MUL(104, $$)")
        self.emit_opcode(ADD)
        self.emit_push(self.PIXEL_DATA_START)
        self.emit_opcode(ADD)
        self.emit_opcode(MLOAD)
        # then move over all but the first byte
        self.emit_raw("SHR(%d, $$)" % (8 * 31))

        self.update_stack(-1, 'get dot')

    def visit_binary_op_node(self, node):
        self.visit(node.right)
        self.visit(node.left)

        ops = {
            '+': ADD,
            '-': SUB,
            '/': SDIV, # TODO: what about zero?
            '*': MUL,
        }
        self.emit_opcode(ops[node.value])

        self.update_stack(-1, 'binary op')

    def visit_number_node(self, node):
        self.emit_push(node.value)

        self.update_stack(1, 'push number literal')

    def visit_noop_node(self, node):
        pass #NOOP


    ####
    # Infos
    def get_procedure_block_dependencies(self, node):
        with self.stashed_state_to_get_block_dependencies():
            self.visit_procedure_definition_node(node)
            return self.block_dependencies
