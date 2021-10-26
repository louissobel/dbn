from parser.structures.ast_nodes import *
from parser import DBNAstVisitor

from .structures import ProcedureDefinition

class SymbolCollector(DBNAstVisitor):

    def collect_symbols(self, node):
        self.procedure_definitions = []
        self.variables = set()
        self.called_procedures = set()

        self.visit(node)
        return self

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
        self.called_procedures.add(node.procedure_name.value)

        for arg in node.args:
            self.visit(arg)

    def visit_procedure_definition_node(self, node):
        formal_args = []
        for arg in node.args:
            formal_args.append(arg.value)
            self.variables.add(arg.value)

        self.procedure_definitions.append(ProcedureDefinition(
            node,
            node.procedure_name.value,
            formal_args,
            node.procedure_type == 'number',
        ))

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
