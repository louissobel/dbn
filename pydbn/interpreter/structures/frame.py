
class DBNFrame(object):
    
    def __init__(self, parent=None, base_line_no=-1, return_pointer=-1, depth=0):
        self.base_line_no = base_line_no
        self.parent = parent
        self.env = {}

        self.stack = []
        self.return_pointer = return_pointer

        self.depth = depth

    def lookup_variable(self, key, default=None):
        """
        searches this first, then parents
        """
        try:
            return self.env[key]
        except KeyError:
            if self.parent is None:
                return default
            else:
                return self.parent.lookup_variable(key, default)
    
    def bind_variable(self, key, value):
        self.env[key] = value

    def bind_variables(self, **dct):
        self.env.update(dct)

    def __str__(self):
        return "[Frame|rp:%d|stack:%s|env:%s|parent:%s]" % (
            self.return_pointer,
            str(self.stack),
            str(self.env),
            str(self.parent),
        )
