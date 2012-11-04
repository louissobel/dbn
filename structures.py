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
        
        
class DBNStateWrapper():
    
    
    def __init__(self, state):
        self.change_state(state)
    
    def change_state(self, state):
        self.cursor = state
        self.start = self.get_start()
        self.end = self.get_end()
        self.length = None # to trigger a cache refrese
        self.cursor_index = self._find_index()
        
    def __len__(self):
        if self.length is not None:
            return self.length
        else:
            i = 0
            stepper = self.start
            while stepper.next is not None:
                i += 1
                stepper = stepper.next
            self.length = i
            return i
    
    def _find_index(self):
        # count backwards!
        index = 0
        pos = self.cursor
        while pos.previous is not None:
            pos = pos.previous
            index += 1
        return index
            
    def next_scrub(self):
        """
        advances the cursor one 'scrub step'
        a 'scrub step' is to the last state
        in a set of common line numbers
        
        if cursor is on the last of some numbers,
        will go to the next.
        
        look:
        
        5 5 5 5 5 6 6 6 6 6
            ^
                *
                
        5 5 5 5 5 6 6 6 6 6
                ^
                          *
        
        will return None if there isn't one
        """
        current_line_no = self.cursor.line_no
        # ok lets step
        next = self.cursor.next # OK with this throwing attribute
        raise NotImplementedError
        
    def get_start(self):
        """
        returns the first state of the cursor
        """
        first = self.cursor
        while first.previous is not None:
            first = first.previous
        return first.next #  because the first one is a nubile state
        
    def get_end(self):
        """
        retusnt the last state of the cursor
        """
        last = self.cursor
        while last.next is not None:
            last = last.next
        return last
    
    def rewind(self):
        """
        changes cursor to be the first
        """ 
        self.cursor = self.start
        self.cursor_index = 0
        
    def fast_forward(self):
        """
        changes cursor to be the last
        """
        self.cursor = self.end
        self.cursor_index = len(self)
        
    def seek(self, n):
        """
        moves the cursor to the nth state (1 indexed)
        raises IndexError if n is out of range
        """
        self.rewind()
        for i in range(0,n):
            try:
                self.cursor = self.cursor.next
                self.cursor_index += 1
            except AttributeError: # if cursor is None
                raise IndexError
        if self.cursor is None:
            raise IndexError
        # ok.
        
            
        