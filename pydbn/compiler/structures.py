"""
bytecode class
"""

class Bytecode(object):
    """
    represents one bytecode
    """

    def __init__(self, op, arg=None):
        self.op = op

        if isinstance(arg, Label):
            self.has_label = True
            self.label = arg
        else:
            self.has_label = False
            self.arg = '_' if arg is None else str(arg)

    def __str__(self):
        return "%s %s" % (self.op, self.arg)

    def __repr__(self):
        return "BC(%s)" % str(self)

    def __eq__(self, other):
        return self.op == other.op and self.arg == other.arg

class Label(object):
    """
    A label in the compiler
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "L:%s" % self.name

