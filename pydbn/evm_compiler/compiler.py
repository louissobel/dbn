import sys

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
    Memory layout (will need to change with base64, etc?)
    0x0000 : [] 
    0x0020 : []
    0x0040 : [bitmap starts...]
    .... (bitmap is 40 + 14 + 404 + 101*104 = 10962 long)
    0x2B20 : Pen
    0x2B40 : Env Pointer
    0x2B60 : Env start
    """
    BITMAP_BASE = 0x40
    PIXEL_DATA_START = BITMAP_BASE + 14 + 40 + 404
    PEN_ADDRESS = 0x2B20

    ENV_POINTER_ADDRESS = 0x2B40
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


    def generate_label(self, prefix):
        """
        generates a unique label for given prefix
        """
        count = self.label_prefix_counts.get(prefix, 0)
        label_name = "dbnDrawCompiled0%s%d" % (prefix, count)
        self.label_prefix_counts[prefix] = count + 1
        return label_name

    def compile(self, node, **kwargs):
        symbol_collector = SymbolCollector().collect_symbols(node)
        self.symbol_mapping = dict(
            (s, i) for i, s in enumerate(symbol_collector.variables)
        )
        print(self.symbol_mapping, file=sys.stderr)

        self.procedure_definitions_by_name = {
            dfn.name : dfn for dfn in symbol_collector.procedure_definitions
        }
        print(self.procedure_definitions_by_name, file=sys.stderr)

        self.lines = []
        self.label_prefix_counts = {}

        self.visit(node)
        return "\n".join(self.lines)


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
        # TODO: debug node where we spit this out for real?
        self.emit_newline()
        self.emit_comment("line number: %d" % line_no)
        return self

    def emit_raw(self, data):
        self.lines.append(data)

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

        # Emit some comments about the memory layout?
        self.visit_block_node(node)

        self.emit_newline()
        self.emit_comment("return to caller control")
        self.emit_jump("dbnDrawComplete")
        self.emit_comment(";;;;;;; End DBN Drawing")
        self.emit_newline()

    def visit_block_node(self, node):
        for sub_node in node.children:
            self.visit(sub_node)

    def visit_set_node(self, node):
        self.emit_line_no(node.line_no)

        left = node.left

        # If left is a bracket, we're setting a single dot
        if   isinstance(left, DBNBracketNode):
            # Peer inside the bracket
            bracket_left, bracket_right = left.children

            label = self.generate_label("postSetCommand")
            self.emit_push_label(label) # return
            self.visit(node.right)      # color
            self.visit(bracket_left)    # x
            self.emit_push(self.PIXEL_DATA_START)
            self.visit(bracket_right)   # y
            self.emit_jump('setCommand')
            self.emit_label(label)

        elif isinstance(left, DBNWordNode):
            # Skip setting the bitmap for now...

            # Get the value on the stack
            self.visit(node.right)
            self.handle_env_set(left.value)

    def visit_word_node(self, node):
        self.handle_env_get(node.value)

    def handle_env_set(self, symbol):
        """
        assumes value to set is top of stack
        """

        # TODO: better error message for unexpected symbol
        index = self.symbol_mapping[symbol]

        self.emit_load_env_base()  # [env_base|value

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

    def handle_env_get_assuming_present(self, symbol):
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
        self.handle_env_set(node.var.value)

        # and then the body itself!
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
            """
            Ok: calling discipline
            Caller:
             - pushes return address on the stack
             - mints a fresh environment
                - bitmap is zero
                - parent is set
             - copies in formal args
            Callee:
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

            # Get args on stack (in reverse order)
            for arg in reversed(node.args):
                self.visit(arg)

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
            if not dfn.args:
                self.emit_push(0)           # [0|new_env_base
            else:
                for i, symbol in enumerate(dfn.args):
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
            for symbol in dfn.args:                                 # [new_env_base|arg*
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

    def handle_builtin_pen(self, node):
        if len(node.args) != 1:
            raise self.invalid_argument_count("Pen", 1, len(node.args))

        self.emit_comment("set Pen")
        self.visit(node.args[0])
        self.emit_raw("MSTORE(%d, $$)" % self.PEN_ADDRESS)

    def handle_builtin_line(self, node):
        # first, return address
        label = self.generate_label("postLineCall")

        self.emit_push_label(label)
        self.emit_push(self.PIXEL_DATA_START)
        self.emit_raw("MLOAD(%d) ; get pen" % self.PEN_ADDRESS)

        if len(node.args) != 4:
            raise self.invalid_argument_count("Line", 4, len(node.args))

        # get the arguments on the stack in reverse order
        for arg_node in reversed(node.args):
            self.visit(arg_node)

        # run the command!
        self.emit_jump('lineCommand')
        self.emit_label(label)

    def handle_builtin_paper(self, node):
        label = self.generate_label("postPaperCall")

        self.emit_push_label(label)
        self.emit_push(self.PIXEL_DATA_START)

        if len(node.args) != 1:
            raise self.invalid_argument_count("Paper", 1, len(node.args))

        self.visit(node.args[0])

        # run the command!
        self.emit_jump('paperCommand')
        self.emit_label(label)

    def invalid_argument_count(self, command_name, expected, got):
        return ValueError("%s expects %d arguments, got %d")

    def visit_procedure_definition_node(self, node):
        self.emit_line_no(node.line_no)

        procedure_start_label = self.generate_label('userProcedureDefinition')
        self.procedure_definitions_by_name[node.procedure_name.value].label = procedure_start_label

        after_procedure_label = self.generate_label('afterUserProcedureDefinition')

        # Move execution to after the procedure body
        self.emit_jump(after_procedure_label)

        self.emit_label(procedure_start_label)

        # TODO: while we're visiting the body, we can
        # _assume_ that the formal args are set, we should track that
        self.visit(node.body)

        # TODO: emit default return value if it is a Number?
        # self.add('LOAD_INTEGER', 0)
        self.emit_raw('JUMP($$)')

        self.emit_label(after_procedure_label)

    def visit_value_node(self, node):
        self.emit_line_no(node.line_no)
        self.visit(node.result)
        self.add('RETURN')

    def visit_load_node(self, node):
        self.emit_line_no(node.line_no)
        self.add('LOAD_CODE', node.value)

    def visit_bracket_node(self, node):
        self.visit(node.right)
        self.visit(node.left)

        self.add('GET_DOT')

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

    def visit_number_node(self, node):
        self.emit_push(node.value)

    def visit_noop_node(self, node):
        pass #NOOP
