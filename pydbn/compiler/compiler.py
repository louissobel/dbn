import structures
from parser.structures.ast_nodes import *
from parser import DBNAstVisitor


def compile(node, *args, **kwargs):
    compiler = DBNCompiler()
    return compiler.compile(node, *args, **kwargs)


class DBNCompiler(DBNAstVisitor):

    def add(self, code, arg='_'):
        self.code.append(structures.Bytecode(code, arg))
        return self

    def add_set_line_no_unless_module(self, line_no):
        if not self.module:
            self.add('SET_LINE_NO', line_no)

    def generate_label(self, prefix):
        """
        generates a unique label for given prefix
        """
        count = self.label_prefix_counts.get(prefix, 0)
        label_name = "%s_%d" % (prefix, count)
        self.label_prefix_counts[prefix] = count + 1
        return structures.Label(label_name)

    def add_label(self, label):
        """
        does not generate a label
        """
        self.code.append(label)

    def compile(self, node, **kwargs):
        self.code = []
        self.module = kwargs.get('module', False)
        self.label_prefix_counts = {}

        self.visit(node)
        return self.code

    ####
    # Visitor methods

    def visit_program_node(self, node):
        self.visit_block_node(node)
        if not self.module:
            self.add('END')

    def visit_block_node(self, node):
        for sub_node in node.children:
            self.visit(sub_node)

    def visit_set_node(self, node):
        self.add_set_line_no_unless_module(node.line_no)

        self.visit(node.right)
        left = node.left

        # If left is a bracket, its a store_bracket op
        if   isinstance(left, DBNBracketNode):
            # Peer inside the bracket
            bracket_left, bracket_right = left.children

            self.visit(bracket_right)
            self.visit(bracket_left)

            self.add('SET_DOT')

        elif isinstance(left, DBNWordNode):
            self.add('STORE', left.value)

    def visit_repeat_node(self, node):
        self.add_set_line_no_unless_module(node.line_no)

        self.visit(node.end)
        self.visit(node.start)

        # body entry - [end, current]
        body_entry_label = self.generate_label('repeat_body_entry')
        repeat_end_label = self.generate_label('repeat_end')

        # mark current location
        self.add_label(body_entry_label)

        # dup current for store
        self.add('DUP_TOPX', 1)
        self.add('STORE', node.var.value)

        self.visit(node.body)

        # Comparison
        self.add('DUP_TOPX', 2)
        self.add('COMPARE_SAME')
        # now stack is [end, current, current==end]
        # if current is the same as end, lets GTFO
        self.add('POP_JUMP_IF_TRUE', repeat_end_label)

        # if we are here, we need either to increment or decrement
        # going to deletegate this to an opcode
        self.add('REPEAT_STEP')
        self.add('JUMP', body_entry_label)

        # ok, now this stuff is cleanup - pop away
        self.add_label(repeat_end_label)
        self.add('POP_TOPX', 2)

    def visit_question_node(self, node):
        self.add_set_line_no_unless_module(node.line_no)

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

    def visit_command_node(self, node):
        self.add_set_line_no_unless_module(node.line_no)

        # get the children on the stack in reverse order
        for arg_node in reversed(node.args):
            self.visit(arg_node)

        # load the name of the command
        self.add('LOAD_STRING', node.value)

        # run the command!
        self.add('COMMAND', len(node.args))

        # command return value always gets thrown away
        self.add('POP_TOPX', 1)

    def visit_procedure_definition_node(self, node):
        self.add_set_line_no_unless_module(node.line_no)

        procedure_start_label = self.generate_label('procedure_%s_definition_%s' % (node.value, node.procedure_name.value))
        after_procedure_label = self.generate_label('after_procedure_definition')

        for arg in reversed(node.args):
            self.add('LOAD_STRING', arg.value)
        self.add('LOAD_STRING', node.procedure_name.value)

        self.add('LOAD_INTEGER', procedure_start_label)
        self.add('LOAD_STRING', node.value)
        self.add('DEFINE_PROCEDURE', len(node.args))

        # Move execution to after the procedure body
        self.add('JUMP', after_procedure_label)

        self.add_label(procedure_start_label)
        self.visit(node.body)

        # Implicitly add fallback return 0
        self.add('LOAD_INTEGER', 0)
        self.add('RETURN')

        self.add_label(after_procedure_label)

    def visit_load_node(self, node):
        self.add_set_line_no_unless_module(node.line_no)
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
        self.add('LOAD_INTEGER', node.value)

    def visit_word_node(self, node):
        self.add('LOAD', node.value)

    def visit_noop_node(self, node):
        pass #NOOP
