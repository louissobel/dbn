from parser.structures.ast_nodes import *
from parser import DBNAstVisitor

from .structures import ProcedureDefinition, CompileError

class SymbolCollector(DBNAstVisitor):

    def collect_symbols(self, node):
        self.procedure_definitions = []
        self.variables = set()
        self.called_procedures = set()

        self._procedure_definition_lines = {}

        self.visit(node)

        if len(self.variables) > 255:
            raise CompileError(
                "Too many unique variable names (%d)! You can only use up to 255. Try reusing some." % (
                    len(self.variables),
                ),
                None,
            )

        overloaded = self.variables & {dfn.name for dfn in self.procedure_definitions}
        if overloaded:
            raising = overloaded.pop()
            dfn_line = self._procedure_definition_lines[raising]

            raise CompileError(
                "\"%s\" is used both as the name of a variable and also as the name of a command or number" % (
                    raising,
                ),
                dfn_line,
                line_number_in_message=True,
            )

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

        name = node.procedure_name.value

        # Check that we only define a procedure once
        if name in self._procedure_definition_lines:
            raise CompileError(
                "Defining a command or number \"%s\" twice: first at line %d and then again at line %d" % (
                    name,
                    self._procedure_definition_lines[name],
                    node.line_no,
                ),
                node.line_no,
                related_line=self._procedure_definition_lines[name],
                line_number_in_message=True,
            )
        self._procedure_definition_lines[name] = node.line_no

        # Check that all formal args are unique
        seen_formal_args = set()
        for arg in formal_args:
            if arg in seen_formal_args:
                raise CompileError(
                    "Definition of %s \"%s\" has duplicate argument names (\"%s\")" % (
                        node.procedure_type,
                        name,
                        arg
                    ),
                    node.line_no,
                )
            seen_formal_args.add(arg)


        self.procedure_definitions.append(ProcedureDefinition(
            node,
            name,
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
        raise CompileError(
            "Load not supported in this version of DBN",
            node.line_no,
        )
