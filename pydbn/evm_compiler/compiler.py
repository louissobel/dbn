from . import structures
from parser.structures.ast_nodes import *
from parser import DBNAstVisitor


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
    """
    BITMAP_BASE = 0x40
    PIXEL_DATA_START = BITMAP_BASE + 14 + 40 + 404
    PEN_ADDRESS = 0x2B20


    # other constants
    INITIAL_PEN_VALUE = 100


    def generate_label(self, prefix):
        """
        generates a unique label for given prefix
        """
        count = self.label_prefix_counts.get(prefix, 0)
        label_name = "dbnDrawCompiled0%s%d" % (prefix, count)
        self.label_prefix_counts[prefix] = count + 1
        return label_name

    def add_label(self, label):
        """
        does not generate a label
        """
        self.code.append(label)

    def compile(self, node, **kwargs):
        self.lines = []
        self.label_prefix_counts = {}

        self.emit_comment("DBN drawing")
        self.emit_newline()

        self.visit(node)
        return "\n".join(self.lines)


    def emit_comment(self, comment):
        # TODO: escape the comment?
        self.lines.append("; %s" % comment)

    def emit_newline(self):
        self.lines.append("")

    def emit_opcode(self, opcode):
        self.lines.append(opcode)
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
        self.emit_label('dbnDraw')

        self.emit_comment("initialize pen to %d" % self.INITIAL_PEN_VALUE)
        self.emit_raw("MSTORE(%d, %d)" % (self.PEN_ADDRESS, self.INITIAL_PEN_VALUE))


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
            self.add('STORE', left.value)

    def visit_repeat_node(self, node):
        self.emit_line_no(node.line_no)

        self.visit(node.end)
        self.visit(node.start)

        # body entry - [end, current]
        body_entry_label = self.generate_label('repeat_body_entry')

        # mark current location
        self.add_label(body_entry_label)

        # dup current for store
        self.add('DUP_TOPX', 1)
        self.add('STORE', node.var.value)

        self.visit(node.body)

        # logic for repeat end is done inside interpreter
        self.add('REPEAT_STEP', body_entry_label)

    def visit_question_node(self, node):
        self.emit_line_no(node.line_no)

        self.visit(node.right)
        self.visit(node.left)

        questions = {
            'Same': ('COMPARE_SAME', 'POP_JUMP_IF_FALSE'),
            'NotSame': ('COMPARE_SAME', 'POP_JUMP_IF_TRUE'),
            'Smaller': ('COMPARE_SMALLER', 'POP_JUMP_IF_FALSE'),
            'NotSmaller': ('COMPARE_SMALLER', 'POP_JUMP_IF_TRUE'),
        }
        compare_op, jump_op = questions[node.value]
        self.add(compare_op)

        after_body_label = self.generate_label('question_after_body')
        self.add(jump_op, after_body_label)

        self.visit(node.body)
        self.add_label(after_body_label)

    def visit_procedure_call_node(self, node):
        if node.procedure_type == 'command':
            self.emit_line_no(node.line_no)
        else:
            # TODO: handle numbers
            raise ValueError("can only handle commands right now!")

        if node.procedure_name.value == "Line":
            self.handle_builtin_line(node)
        elif node.procedure_name.value == "Pen":
            self.handle_builtin_pen(node)
        else:
            # TODO: clearly, handle other commands
            raise ValueError("can only handle Line / Pen right now")

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

    def invalid_argument_count(self, command_name, expected, got):
        return ValueError("%s expects %d arguments, got %d")

    def visit_procedure_definition_node(self, node):
        self.emit_line_no(node.line_no)

        procedure_start_label = self.generate_label('procedure_%s_definition_%s' % (node.value, node.procedure_name.value))
        after_procedure_label = self.generate_label('after_procedure_definition')

        for arg in reversed(node.args):
            self.add('LOAD_STRING', arg.value)
        self.add('LOAD_STRING', node.procedure_name.value)

        self.add('LOAD_INTEGER', procedure_start_label)
        self.add('LOAD_STRING', node.procedure_type)
        self.add('DEFINE_PROCEDURE', len(node.args))

        # Move execution to after the procedure body
        self.add('JUMP', after_procedure_label)

        self.add_label(procedure_start_label)
        self.visit(node.body)

        # Implicitly add fallback return 0
        self.add('LOAD_INTEGER', 0)
        self.add('RETURN')

        self.add_label(after_procedure_label)

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
            '+': 'BINARY_ADD',
            '-': 'BINARY_SUB',
            '/': 'BINARY_DIV',
            '*': 'BINARY_MUL',
        }
        self.add(ops[node.value])

    def visit_number_node(self, node):
        self.emit_push(node.value)

    def visit_word_node(self, node):
        self.add('LOAD', node.value)

    def visit_noop_node(self, node):
        pass #NOOP
