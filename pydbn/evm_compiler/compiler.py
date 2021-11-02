import sys
import contextlib

from . import structures
from .structures import CompileError
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
        if self.getting_scope_dependencies:
            prefix = '>>>> Getting Scope Dependencies: '
        if self.verbose:
            print(prefix + str(message), file=sys.stderr)

    def compile(self, node, metadata=structures.EMPTY_METADATA):
        self.lines = []
        self.label_prefix_counts = {}
        self.line_no = 0
        self.no_env = False

        # stack_size is relative to command / program scope
        self.stack_size = 0
        self.getting_scope_dependencies = False
        self.getting_root_scope_dependencies = False
        self.root_stack_slots = []

        self.current_procedure_definition = None

        symbol_collector = SymbolCollector().collect_symbols(node)
        self.symbol_mapping = dict(
            (s, i) for i, s in enumerate(symbol_collector.variables)
        )
        self.log('Symbol Mapping: %s' % self.symbol_mapping)

        self.setup_builtins()

        # Initially, we _know_ all variables are local.
        # if we are not in a command then they all default to present
        self.symbol_directory = structures.SymbolDirectory().with_locals(
            symbol_collector.variables
        )

        self.procedure_definitions = symbol_collector.procedure_definitions
        self.procedure_definitions_by_name = {
            dfn.name : dfn for dfn in symbol_collector.procedure_definitions
        }
        self.log('Procedures: %s' % self.procedure_definitions_by_name)

        # Optimize
        self._allocate_stack_variables(node)


        self.visit(node)

        # Special metadata functions
        self.emit_metadata(metadata)

        return "\n".join(self.lines)

    def _allocate_stack_variables(self, node):
       # Stack variable allocation decisions
        for dfn in self.procedure_definitions:
            dfn.scope_dependencies = self.get_scope_dependencies(dfn.node)
            dfn.local_env_args, dfn.stack_slots, dfn.needs_env = (
                self.make_variable_location_decisions_for(
                    dfn.scope_dependencies,
                    dfn.args,
                    dfn.name,
                )
            )
        self._clear_dfn_labels()

        # Ok — make a _top level_ stack allocation decision
        root_scope_dependencies = self.get_scope_dependencies(node, root=True)
        self._clear_dfn_labels()

        root_locals_env_args, root_stack_slots, _ = (
            self.make_variable_location_decisions_for(
                root_scope_dependencies,
                [],
                '<root>'
            )
        )
        if root_locals_env_args or any(slot.is_arg for slot in root_stack_slots):
            raise AssertionError('we are not passing any args, so these should not get set')

        self.root_stack_slots = root_stack_slots
        self.symbol_directory = self.symbol_directory.with_stack(
            {s.symbol: i for (i, s) in enumerate(reversed(root_stack_slots))}
        )

    def _clear_dfn_labels(self):
        for dfn in self.procedure_definitions:
            dfn.label = None
            dfn.epilogue_label = None

    def setup_builtins(self):
        line = structures.BuiltinProcedure('Line', 'command', 4, self.handle_builtin_line)
        paper = structures.BuiltinProcedure('Paper', 'command', 1, self.handle_builtin_paper)
        pen = structures.BuiltinProcedure('Pen', 'command', 1, self.handle_builtin_pen)

        debugger = structures.BuiltinProcedure('DEBUGGER', 'command', 0, self.handle_builtin_debugger)
        self.builtin_procedures = {
            'Line': line,
            'Paper': paper,
            'Pen': pen,
            'DEBUGGER': debugger,
        }

    @contextlib.contextmanager
    def new_symbol_directory(self, new_directory, why='unknown'):
        old_directory = self.symbol_directory
        self.symbol_directory = new_directory
        self.log("Pushing new directory (%s): %s" % (why, self.symbol_directory))
        yield
        self.symbol_directory = old_directory

    @contextlib.contextmanager
    def stashed_state_to_get_scope_dependencies(self, root=False):
        old_lines = self.lines
        self.lines = []

        old_label_prefix_counts = self.label_prefix_counts
        self.label_prefix_counts = {}

        self.getting_scope_dependencies = True
        if root:
            self.getting_root_scope_dependencies = True
        self.scope_dependencies = structures.ScopeDependencies()
        yield
        self.scope_dependencies = None
        if root:
            self.getting_root_scope_dependencies = False
        self.getting_scope_dependencies = False

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

    def emit_dup(self, depth):
        self.emit_opcode([
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
        ][depth-1])
        return self

    def emit_swap(self, depth):
        self.emit_opcode([
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
        ][depth-1])
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
            # we validate there's not too many variables at the start of compilation
            raise AssertionError("index mustn't be greater than 255!! too many variables?")

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
        # TODO: what do we want to do with these errors?
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

        self.emit_newline()
        self.emit_comment('placeholders for root-level stack vars')
        for _ in self.root_stack_slots:
            self.emit_push(0); # TODO: I can shrink this in size...
        self.update_stack(len(self.root_stack_slots), 'root stack slots')

        self.visit_block_node(node)

        self.emit_newline()
        self.emit_comment('clear away root-level stack vars')
        for _ in self.root_stack_slots:
            self.emit_opcode(POP);
        self.update_stack(-1 * len(self.root_stack_slots), 'clearing root stack slots')

        self.emit_newline()
        self.emit_comment("return to caller control")
        self.emit_jump("dbnDrawComplete")
        self.emit_comment(";;;;;;; End DBN Drawing")
        self.emit_newline()
        self.emit_opcode(STOP)
        self.emit_newline()

    def visit_block_node(self, node):
        symbol_directory_for_this_block = self.symbol_directory.copy()
        with self.new_symbol_directory(symbol_directory_for_this_block, 'block'):
            for sub_node in node.children:
                self.visit(sub_node)

                # If we set a variable in a block, for the remainder of the block
                # we can later assume that that variable is present
                # (and use optimized read path)
                if self.node_is_variable_set(sub_node):
                    symbol = sub_node.left.value
                    if symbol_directory_for_this_block.location_for(symbol).is_global():
                        symbol_directory_for_this_block.set_local(symbol)
                        self.log("Update directory for set (%s) in block: %s" % (symbol, self.symbol_directory))

                elif self.node_is_value(sub_node):
                    # then actually, we're done.
                    # TODO: emit some kind of warning about the dead code?
                    break

    def node_is_variable_set(self, node):
        return isinstance(node, DBNSetNode) and isinstance(node.left, DBNWordNode)

    def node_is_value(self, node):
        return isinstance(node, DBNValueNode)

    def visit_set_node(self, node):
        self.emit_line_no(node.line_no)

        left = node.left

        # If left is a bracket, we're setting a single dot
        if   isinstance(left, DBNBracketNode):
            # Peer inside the bracket
            bracket_left, bracket_right = left.children

            label = self.generate_label("postSetCommand")
            self.emit_push_label(label) # return
            self.update_stack(1, "Set command internal (Return)")

            self.visit(node.right)      # color
            self.visit(bracket_left)    # x

            self.emit_push(self.PIXEL_DATA_START)
            self.update_stack(1, "Set command internal (pixeldata)")

            self.visit(bracket_right)   # y

            self.emit_jump('setCommand')
            self.emit_label(label)

            self.update_stack(-5, 'set dot')

        elif isinstance(left, DBNWordNode):
            # Get the value on the stack
            self.visit(node.right)

            # If we already know the symbol is local,
            # then we don't need  to flip the bitmap.
            # but regardless, all sets are "local" for purposes
            # of tracking dependencies
            symbol = left.value

            if self.getting_scope_dependencies:
                self.scope_dependencies.variable_sets.append(
                    structures.ScopeDependencies.VariableAccess(
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
                self.handle_env_set_stack(location)
            else:
                self.handle_env_set(symbol)

            self.update_stack(-1, 'set variable')

    def visit_word_node(self, node):
        symbol = node.value

        location = self.symbol_directory.location_for(symbol)

        if self.getting_scope_dependencies:
            self.scope_dependencies.variable_gets.append(
                structures.ScopeDependencies.VariableAccess(
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
            self.handle_env_get_stack(location)
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

    def handle_env_set_stack(self, location):
        # [value|...
        distance = self.stack_size - location.slot - 1 # (-1 to account for value at top)
        if distance > 16:
            raise AssertionError("cannot set stack-stored symbol! too deep!")
        if distance < 1:
            raise AssertionError("cannot set stack-stored symbol! distance somehow < 1...")

        self.emit_swap(distance)
        self.emit_opcode(POP)

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

    def handle_env_get_stack(self, location):
        distance = self.stack_size - location.slot
        if distance > 16:
            raise AssertionError("cannot access stack-stored symbol! too deep!")
        if distance < 1:
            raise AssertionError("cannot access stack-stored symbol! distance somehow < 1...")

        self.emit_dup(distance)

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
        if location.is_local():
            # Then this is already a local variable and I don't need to do
            # anything pre-entry
            new_location = location
        elif location.is_stack():
            # Same as above, I don't need to do anything
            new_location = location
        else:
            # For the duration of the block, I can now consider
            # this a local variable. Pre-loop entry, let's make
            # sure the bitmap is set
            new_location = structures.SymbolDirectory.SymbolLocation.local()

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
        # The repeat owns its own copy of "value" even if it is already stored elsewhere
        # on the stack. This ensures that writes to the value inside the loop
        # get overwritten on loop entry (meaning the last loop will still set OK)
        # [step|value|end
        self.update_stack(1, 'repeat body')
        self.emit_label(body_entry_label)

        # set value in the environment
        self.update_stack(1, 'repeat local value copy')
        self.emit_opcode(DUP2)

        # For dependency tracking purposes, this is a regular set
        if self.getting_scope_dependencies:
            self.scope_dependencies.variable_sets.append(
                structures.ScopeDependencies.VariableAccess(
                    var_symbol,
                    self.stack_size,
                    False,
                    self.line_no,
                )
            )

        self.emit_comment('  --> setting repeat iteration variable %s' % var_symbol)
        if new_location.is_local():
            self.handle_env_set_local(var_symbol)
        else:
            self.handle_env_set_stack(new_location)
        self.update_stack(-1, 'repeat local value set')

        # and then the body itself!
        # while we visit it, we _know_ the var is set
        with self.new_symbol_directory(self.symbol_directory.with_locations({var_symbol: new_location}), 'repeat'):
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

        procedure_name = node.procedure_name.value

        builtin = self.builtin_procedures.get(procedure_name)
        if builtin is not None:
            return self.handle_builtin(builtin, node)

        if self.getting_scope_dependencies:
            self.scope_dependencies.procedures_called.append(
                structures.ScopeDependencies.VariableAccess(
                    procedure_name,
                    self.stack_size,
                    True,
                    self.line_no,
                )
            )

        """
        Caller:
            - pushes return address on the stack
            - args on stack
              - first, reversed stack slots
              - next, reversed env args
            - ex: Foo A B C D (C D local, A B _ stack slots):
               --> [C|D|A|B|_|ret
            - jumps to procedure
        Callee:
            - mints a fresh environment
               - bitmap is zero
               - parent is set
             - sets up its stack slots
             - copies local vars ito the new environment
         - promises to pop any stack vars
         - pops away the environment
         - promises to jump back to return address!
        Caller:
         
        """
        try:
            dfn = self.procedure_definitions_by_name[procedure_name]
        except KeyError:
            raise CompileError(
                "Calling undefined %s \"%s\"" % (
                    node.procedure_type,
                    procedure_name,
                ),
                self.line_no,
            )

        if dfn.label is None:
            raise CompileError(
                "Calling %s \"%s\" (at line %d) before it is defined (down at line %d)" % (
                    node.procedure_type,
                    procedure_name,
                    self.line_no,
                    dfn.node.line_no,
                ),
                self.line_no,
                related_line=dfn.node.line_no,
                line_number_in_message=True,
            )

        if len(node.args) != len(dfn.args):
            raise CompileError(
                "Calling %s \"%s\" (at line %d) with %d %s, but it is defined (at line %d) with %d" % (
                    node.procedure_type,
                    procedure_name,
                    self.line_no,
                    len(node.args),
                    'argument' if len(node.args) == 1 else 'arguments',
                    dfn.node.line_no,
                    len(dfn.args),
                ),
                self.line_no,
                related_line=dfn.node.line_no,
                line_number_in_message=True,
            )

        if dfn.is_number and node.procedure_type == 'command':
            raise CompileError(
                "Cannot use number \"%s\" (defined at line %d) as a command" % (
                    procedure_name,
                    dfn.node.line_no,
                ),
                self.line_no,
                related_line=dfn.node.line_no,
            )

        if not dfn.is_number and node.procedure_type == 'number':
            raise CompileError(
                "Cannot use command \"%s\" (defined at line %d) as a number" % (
                    procedure_name,
                    dfn.node.line_no,
                ),
                self.line_no,
                related_line=dfn.node.line_no,
            )

        post_call_label = self.generate_label('postUserProcedureCall')

        # Return value
        self.emit_push_label(post_call_label)
        self.update_stack(1, 'Command Return Destination')

        arg_nodes_by_name = dict(zip(dfn.args, node.args))
        # First, stack slots (reversed)
        # TODO: move these to the definition :)
        self.log("PROC CALL found stack slots:%s locals:%s" % (dfn.stack_slots, dfn.local_env_args))
        for slot in reversed(dfn.stack_slots):
            if slot.is_arg:
                self.visit(arg_nodes_by_name[slot.symbol])
            else:
                # it's a placeholder, so let's just emit the cheapest, smallest
                # instruction (one from the class W_base)
                # TODO: should we instead set to zero somehow? (CALLDATASIZE?)
                # TODO: we _could_ put the placeholders in the definition,
                # but it's simpler from a stack-allocation perspective to do it here.
                self.emit_opcode(ADDRESS)
                self.update_stack(1, 'command stack slot placeholder')

        # Then, local env args (also reversed)
        for arg in reversed(dfn.local_env_args):
            self.visit(arg_nodes_by_name[arg])

        self.emit_jump(dfn.label)
        self.emit_label(post_call_label)

        # TODO: this maybe needs to consider any noop arg optimizations we make...
        stack_consumed = len(dfn.stack_slots) + len(dfn.local_env_args) + 1 # + 1 for return address
        if dfn.is_number:
            # one less stack slot is consumed if we're calling a "Number":
            # it guarantees to leave one value on the stack
            stack_consumed -= 1

        self.update_stack(-1 * stack_consumed, 'Command return')

    def handle_builtin(self, builtin, node):
        if node.procedure_type != builtin.procedure_type:
            raise CompileError(
                "Cannot use \"%s\" as a %s" % (
                    builtin.name,
                    node.procedure_type,
                ),
                self.line_no,
            )

        if len(node.args) != builtin.argc:
            raise CompileError(
                "%s expects %d %s, got %d" % (
                    builtin.name,
                    builtin.argc,
                    'argument' if builtin.argc == 1 else 'arguments',
                    len(node.args),
                ),
                self.line_no
            )

        self.emit_comment('Calling Builtin: %s' % builtin.name)
        builtin.handler(node)

    def handle_builtin_pen(self, node):
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

        self.visit(node.args[0])

        # run the command!
        self.emit_jump('paperCommand')
        self.emit_label(label)

        self.update_stack(-3, 'Paper')

    def handle_builtin_debugger(self, node):
        self.emit_debug()

    def visit_procedure_definition_node(self, node):
        self.emit_line_no(node.line_no)

        name = node.procedure_name.value
        dfn = self.procedure_definitions_by_name[name]
        if self.current_procedure_definition:
            raise CompileError(
                "Cannot define a %s within a %s definition" % (
                    node.procedure_type,
                    'number' if dfn.is_number else 'command',
                ),
                self.line_no
            )
        self.current_procedure_definition = dfn

        self.emit_comment(';;;; defining %s' % name)

        dfn.label = self.generate_label('userProcedureDefinition')

        if dfn.is_number:
            dfn.epilogue_label = self.generate_label('userProcedureDefinitionEpilogue')

        if self.getting_root_scope_dependencies:
            # Then generating the label is all we do for a procedure definition
            # (leaving behind a stub)
            self.current_procedure_definition = None
            return

        after_procedure_label = self.generate_label('afterUserProcedureDefinition')

        # Move execution to after the procedure body
        self.emit_jump(after_procedure_label)
        self.emit_label(dfn.label)

        with self.fresh_stack('command_def'):

            self.update_stack(
                len(dfn.local_env_args) + len(dfn.stack_slots),
                'command definition starting args',
            )

            if dfn.needs_env:
                self.handle_create_new_env_and_copy_in_locals(dfn.local_env_args)
                self.update_stack(-1 * len(dfn.local_env_args), 'command local env copy')
            else:
                if len(dfn.local_env_args) != 0:
                    raise AssertionError("invariant violated: needs_env is false but there are local_env_vars expected")

            # While we're visiting the body, we _know_
            # that the formal args will always be set
            new_directory = (structures.SymbolDirectory()
                .with_locals(dfn.local_env_args)
                .with_stack({s.symbol: i for (i, s) in enumerate(reversed(dfn.stack_slots))})
            )

            with self.new_symbol_directory(new_directory, 'command_def'):
                # TODO: don't allow Line, Setdot, (field?)
                # or any other side-effectful things in Number!
                self.visit(node.body)

            # Epilogue:
            # - _we_ are responsible for popping the stack variables away
            # - and popping any environment we pushed
            #
            # If this procedure is a Number, then either:
            # - we got here explicitly, in which case stack is [V|slot*|ret
            # - or we fell through, in which case stack is just [slot*|ret
            # We can statically determine based off stack size
            if dfn.is_number:
                # Add the default return
                # Explicit "values" will jump straight to the epilogue
                # TODO: some kind of warning if we use the default?
                # _can_ I statically know???? I don't think so.
                # Runtime warnings???
                self.emit_push(0)
                self.emit_label(dfn.epilogue_label)
                self.update_stack(1, 'Number return value')

                # ok now, we assert that stack size is dfn.stack_slots + 1
                if self.stack_size != len(dfn.stack_slots) + 1:
                    raise AssertionError('at end of number but unexpected stack size %d' % self.stack_size)
                # That said, the _actual_ stack is
                # [V|slots*|ret

                # the depth to which we swap the return value is the same
                # as the number of stack slots:
                #  - [V|ret --> no swap
                #  - [V|slot|slot|slot|ret --> SWAP3 [slot|slot|slot|V|ret
                swap_depth = len(dfn.stack_slots)
                if swap_depth > 0:
                    if swap_depth > 16:
                        raise AssertionError('too many stack slots, retval is unreachable (%d)' % len(dfn.stack_slots))
                    self.emit_swap(swap_depth)

            for _ in range(len(dfn.stack_slots)):
                self.emit_opcode(POP)
            self.update_stack(-1 * len(dfn.stack_slots), 'procedure definition stack slots pop')

            if dfn.needs_env:
                self.handle_pop_env()

            if dfn.is_number:
                # [V|ret
                self.emit_opcode(SWAP1) # [ret|V
                self.update_stack(-1, 'Number return value domain transfer')

            if self.stack_size != 0:
                raise AssertionError("we're about to jump to return, but stack is not empty: %d" % 0)

            self.emit_raw('JUMP($$)')

        self.emit_label(after_procedure_label)
        self.current_procedure_definition = None

    def handle_create_new_env_and_copy_in_locals(self, local_env_args):
        """
        assumes that local_env_args are on the stack in reversed order
        like if local_env_args is [A B C D]
        we expect stack to be [A|B|C|D
        """

        # Build new environment.....
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
        # TODO: (uh... we can do this compile time... I think?)
        # we need to set to zero even if there's env vars
        # because we don't clean up popped environments
        if not local_env_args:
            self.emit_push(0)           # [0|new_env_base
        else:
            for i, symbol in enumerate(local_env_args):
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
        for symbol in local_env_args:                           # [new_env_base|arg*
            index = self.symbol_mapping[symbol] # TODO: better error message?
            self.emit_opcode(SWAP1)                             # [arg*|new_env_base
            self.emit_opcode(DUP2)                              # [new_env_base|arg*|new_env_base
            self.emit_raw("ADD(%d, $$)" % ((2 + index) * 32))   # [env_location|arg*|new_env_base
            self.emit_raw("MSTORE($$, $$)")                     # [new_env_base|arg*
        self.emit_opcode(POP)                                   # [

    def handle_pop_env(self):
        self.emit_load_env_base()
        self.emit_raw("ADD(32, $$)")
        self.emit_opcode(MLOAD)
        self.emit_raw("MSTORE(%d, $$)" % self.ENV_POINTER_ADDRESS)

    def visit_value_node(self, node):
        if self.current_procedure_definition is None:
            raise CompileError(
                "Cannot use Value outside of a Number definition",
                node.line_no,
            )
        if not self.current_procedure_definition.is_number:
            raise CompileError(
                "Can only use Value inside a Number definition, not inside a command",
                node.line_no,
            )

        self.emit_line_no(node.line_no)

        # Stack accounting for "Value" is bespoke.
        # When we're compiling this, the stack is:
        # [x*|slots*|ret
        # (where stack_size, as usual, does not include ret)
        # In execution, we need to:
        # - pop off all x
        # - visit the result
        # - then jump
        #
        # After Value, the stack_size counter needs to be the same as what it was on entry,
        # so that overall block accounting still adds up. This works because Value in effect
        # takes us _out_ of the scope we're doing accounting for, so it's as if it never existed.
        #
        # But, three things:
        #  a) we need the "stack_size" to even determine how much to pop
        #  b) in visiting the result, the stack size needs to be correct
        #     (so any stack slot reads are correct)
        #  c) visiting the result will also implicitly increment the stack_size
        #     (or, it _must_)
        #
        # So we just stash the existing value and restore it on the other side
        stack_size_on_entry = self.stack_size

        # Let's get rid of everything on on top of slots*
        # (this means that Values in nested Repeats pay a size penalty...)
        # And remember that stack_size does _not_ include the return address
        extra_stack_items = self.stack_size - len(self.current_procedure_definition.stack_slots)

        self.log("Reached Value node for dfn: %s, current stack depth: %d, dfn slots: %d, popping: %d" % (
            self.current_procedure_definition,
            self.stack_size,
            len(self.current_procedure_definition.stack_slots),
            extra_stack_items,
        ))

        for _ in range(extra_stack_items):
            self.emit_opcode(POP)

        # Update stack_size so that any stack slot reads in this visit are aligned
        self.update_stack(-1 * extra_stack_items, 'extra stack items popped in Value')

        self.visit(node.result)

        # OK: now we just jump to the function epilogue
        if not self.current_procedure_definition.epilogue_label:
            raise AssertionError("there needs to be an epilogue label set to handle Value..")

        self.emit_jump(self.current_procedure_definition.epilogue_label)

        # Restore the stack
        self.stack_size = stack_size_on_entry

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
    def get_scope_dependencies(self, node, root=False):
        with self.stashed_state_to_get_scope_dependencies(root=root):
            self.visit(node)
            return self.scope_dependencies


    def make_variable_location_decisions_for(self, scope_dependencies, args, name):
        self.log("\n\n[][][][][][][] Stack decision for %s" % name)

        expected_globals = scope_dependencies.globals_expected_by_any_called_function(
            self.procedure_definitions_by_name,
        )

        local_env_args = []
        stack_slots = []

        stack_vars = set()

        all_gets = scope_dependencies.variable_gets
        self.log("---> Gets:")
        for g in all_gets:
            self.log("   • %s" % (g,))
        all_sets = scope_dependencies.variable_sets
        self.log("---> Sets:")
        for s in all_sets:
            self.log("   • %s" % (s,))

        arg_set = set(args)
        non_arg_variables = ({a.symbol for a in all_gets} | {a.symbol for a in all_sets}) - arg_set
        all_symbols = non_arg_variables | arg_set
        symbol_info = {
            s: self._get_symbol_access_info(s, expected_globals, all_gets, all_sets)
            for s in all_symbols
        }

        # Prioritize putting things on the stack
        # that have the deepest accessess
        stack_prioritized_variables = sorted(
            all_symbols,
            key = lambda s : (
                -(symbol_info[s]['deepest_access'] or 0),
                s, # include symbol name to keep sort stable
            )
        )

        self.log("---> Variables (%s)" % stack_prioritized_variables)
        for s in stack_prioritized_variables:
            eligible = self._is_stack_eligible(s, symbol_info[s], nudge=len(stack_slots))
            if s in arg_set:
                if eligible:
                    stack_vars.add(s)
                    stack_slots.append(structures.ProcedureDefinition.StackSlot(True, s))
                else:
                    local_env_args.append(s)
            else:
                if eligible:
                    stack_vars.add(s)
                    stack_slots.append(structures.ProcedureDefinition.StackSlot(False, s))

        # Ok, now one more optimization, do we need an environment at all?
        self.log("--> Environment Decision")
        vars_needing_env = []
        for s in all_symbols:
            if s in stack_vars:
                self.log("   • %s: stack var, doesn't need env" % s)
            else:
                # there's one exception. if the symbol:
                # - is not written to (and is not an arg, which have implicit writes)
                # - is only ever read non-locally
                # then we can effectively delegate to the existing environment
                info = symbol_info[s]
                not_written = (not s in arg_set) and (info['write_count'] == 0)
                only_read_non_locally = (info['read_count'] == info['non_local_read_count'])
                if not_written and only_read_non_locally:
                    self.log("   • %s: not stack var but not arg, never written, and only read non-locally, so does not ned env" % s)
                else:
                    self.log("   • %s: not stack var, needs env" % s)
                    vars_needing_env.append(s)
        
        self.log("--> Need Env to serve %s" % vars_needing_env)


        if len(stack_slots) > 16:
            raise AssertionError("we should never end up with more than 16 stack slots! %d" % len(stack_slots))

        self.log("stack vars: %s" % stack_vars)
        self.log("local env args: %s" % local_env_args)
        self.log("stack slots: %s" % stack_slots)
        self.log("env needed: %s" % bool(vars_needing_env))
        self.log("[][][][][][][]\n\n")

        return (local_env_args, stack_slots, bool(vars_needing_env))

    def _is_stack_eligible(self, symbol, info, nudge=None):
        if nudge is None:
            raise AssertionError("nudge must be specified")

        # an accessed variable is eligible to be stored on the stack IF:
        # - no called procedures expect it to be set
        #   (if we set it, then this applies. if it's read-only though, the below applies)
        # - we never do any non-local gets for it
        # - never gets too far away for gets / sets

        semantically_eligible = (
            (not info['expected_global'])
            and (info['non_local_read_count'] == 0)
        )
        always_reachable = (
            (info['farthest_set'] is None or (info['farthest_set'] + nudge) <= 16)
            and (info['farthest_get'] is None or (info['farthest_get'] + nudge) <= 16)
        )

        self.log("   • %s: expected_global:%s deepest_unnudged_access:%d, writes:%d reads:%d non_local_reads:%d nudged_farthest_get:%s nudged_farthest_set:%s always_reachable:%s semantically_eligible:%s" % (
            symbol,
            info['expected_global'],
            info['deepest_access'],
            info['write_count'],
            info['read_count'],
            info['non_local_read_count'],
            info['farthest_get'] + nudge if info['farthest_get'] else None,
            info['farthest_set'] + nudge if info['farthest_set'] else None,
            always_reachable,
            semantically_eligible,
        ))

        return always_reachable and semantically_eligible

    def _get_symbol_access_info(self, symbol, expected_globals, all_gets, all_sets):
        gets = [a for a in all_gets if a.symbol == symbol]
        sets = [a for a in all_sets if a.symbol == symbol]

        get_distances = [
            (access.stack_size) + 1
            for access in gets
        ]
        set_distances = [
            access.stack_size
            for access in sets
        ]
        farthest_get = max(get_distances) if gets else None
        farthest_set = max(set_distances) if sets else None

        return {
            'farthest_get': farthest_get,
            'farthest_set': farthest_set,
            'expected_global': symbol in expected_globals,
            'read_count': len(gets),
            'write_count': len(sets),
            'non_local_read_count': len([a for a in gets if a.is_global]),
            'deepest_access': max(farthest_get or 0, farthest_set or 0),
        }
