"""
Module to hold DBN data datastructures
"""

class DBNProcedure():
    """
    root class for commands, builtin commands, numbers, builtin numbers
    """
    def __init__(self, argc, line_no=-1):
        self.argc = argc
        
        # line no is where it was defined
        self.line_no = line_no
        
        # defaults to NOT a built in
        self.is_builtin = False
    
    def __str__(self):
        return "[P:%d]" % self.argc
    
    def __repr__(self):
        return self.__str__()


class DBNUserProcedure(DBNProcedure):
    """
    A userspace procedure
    """
    def __init__(self, type_, name, formal_args, body_pointer, line_no=-1):
        DBNProcedure.__init__(self, len(formal_args), line_no)
        self.type = type_
        self.name = name
        self.formal_args = formal_args
        self.body_pointer = body_pointer

    def __str__(self):
        return "[%s%s:%s@%d]" % (self.proc_type, self.name, ','.join(self.formal_args), self.body_pointer)


class DBNBuiltinProcedure(DBNProcedure):
    """
    A builtin command (think Line, Paper, Pen)
    """
    def __init__(self, argc):
        DBNProcedure.__init__(self, argc)
        self.is_builtin = True
    
    def keyword(self):
        raise NotImplementedError
    
    def call(self, interpreter, *args):
        # called with interpreter as first arg, rest as others
        raise NotImplementedError
        
    def __str__(self):
        return "[Native Code]"


    

        