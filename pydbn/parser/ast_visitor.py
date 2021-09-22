"""
Base class for AST visitors
"""
from . import structures


class DBNAstVisitor(object):

    def __init__(self):
        """
        Checks that we have visitor methods for every node type
        """
        for node_class in structures.ast_nodes.AST_NODE_CLASSES:
            visit_method_name = self.__visit_method_name(node_class)

            if not hasattr(self, visit_method_name):
                raise NotImplementedError(
                    "%s is not implemented in %s" % (
                        visit_method_name,
                        self.__class__.__name__
                    )
                )

    def __visit_method_name(self, node):
        """
        live specification for name of visitor method
        node arg can be node or node_class
        """
        template = "visit_%s_node"
        args = (node.type, )
        return template % args

    def visit(self, node):
        """
        dispatched to the proper visit method based on `type` attribute
        """
        visit_method_name = self.__visit_method_name(node)

        # Assumes we have it based on static checking in __init__
        # (So will throw AttributeError if we don't have it)
        visit_method = getattr(self, visit_method_name)

        # Call it
        return visit_method(node)
