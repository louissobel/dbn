"""
Module to hold DBN data datastructures
"""

class DBNVariable:
    def __init__(self, name):
        self.name = name
            
            
class DBNDot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        
class DBNProcedure():
    """
    never created by the parser, only by the evaluation of a command definition node!

    halfy implements the DBNBaseNodeInterface, but really belongs here
    """

    def __init__(self, formal_args, body):
        self.formal_args = formal_args
        self.arg_count = len(formal_args)
        self.body = body

    def __str__(self):
        return "(proc (%s) %s)" % (','.join(self.formal_args), self.body)

    def pprint(self, depth=0, indent=4):
        print "%s(proc" % ((' ' * depth * indent),)
        print "%s(%s)" % ((' ' * (depth+1) * indent), ','.join(self.formal_args))
        self.body.pprint(depth=depth + 1, indent=indent)
        print "%s)" % (' ' * depth * indent)