from parser.structures.ast_nodes import *
from parser import DBNAstVisitor

class SymbolCollector(DBNAstVisitor):

    def collect_symbols(self, node):
        # just collect variables for now, but
        # we could also use this visitor to collect
        # command calls, command definitions?
        self.variables = set()
        self.visit(node)
        return self.variables

    ####
    # Visitor methods

    def visit_program_node(self, node):
        self.visit_block_node(node)

    def visit_block_node(self, node):
        for sub_node in node.children:
            self.visit(sub_node)

    def visit_set_node(self, node):
        self.visit(node.right)
        self.visit(node.left)

    def visit_repeat_node(self, node):
        self.visit(node.var)

        self.visit(node.end)
        self.visit(node.start)
        self.visit(node.body)

    def visit_question_node(self, node):
        self.visit(node.right)
        self.visit(node.left)
        self.visit(node.body)

    def visit_procedure_call_node(self, node):
        for arg in node.args:
            self.visit(arg)

    def visit_procedure_definition_node(self, node):
        for arg in node.args:
            self.visit(arg)

        self.visit(node.body)

    def visit_value_node(self, node):
        self.visit(node.result)

    def visit_bracket_node(self, node):
        self.visit(node.right)
        self.visit(node.left)

    def visit_binary_op_node(self, node):
        self.visit(node.right)
        self.visit(node.left)

    def visit_number_node(self, node):
        pass

    def visit_word_node(self, node):
        self.variables.add(node.value)

    def visit_noop_node(self, node):
        pass

    def visit_load_node(self, node):
        raise RuntimeError("Load not supported for EVM backend")
