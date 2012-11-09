import copy


class StateTransition:
    """
    node in a doubly linked list
    """
    def __init__(self, function=None):
        self.function = function
        self.next = None
        self.previous = None
       
class State:
    
    def __init__(self):
        self.x = 0
        self._next_transition = StateTransition()
        self._previous_transition = StateTransition()
    
    # mutates
    def _set_x(self, n):
        self.x = n
    
    # @Producer
    def set_x(old, n):
        new = copy.copy(old)
        
        new._set_x(n)
                
        new_next_transition = StateTransition()
        new_next_transition.previous = old._next_transition
        old._next_transition.next = new_next_transition
        old._next_transition.function = old.build_forward_set_x(n)
        new._next_transition = new_next_transition
        
        new_previous_transition = StateTransition()
        new_previous_transition.previous = old._previous_transition
        old._previous_transition.next = new_previous_transition
        new_previous_transition.function = old.build_reverse_set_x(n)
        new._previous_transition = new_previous_transition
        
        return new
        
    def build_forward_set_x(previous, n):
        def forward_set_x(next):
            next._set_x(n)
        return forward_set_x
    
    def build_reverse_set_x(previous, n):
        previous_x = previous.x
        def reverse_set_x(next):
            next._set_x(previous_x)
        return reverse_set_x
    
    # Producer
    def next(old):
        new = copy.copy(old)
        
        if old._next_transition.function is None:
            return None
        else:
            old._next_transition.function(new)
            new._next_transition = old._next_transition.next
            new._previous_transition = old._previous_transition.next
            return new
    
    def previous(old):
        new = copy.copy(old)
        
        if old._previous_transition.function is None:
            return None
        else:
            old._previous_transition.function(new)
            new._next_transition = old._next_transition.previous
            new._previous_transition = old._previous_transition.previous
            return new
            

s = State()
print s.x, s
t = s.set_x(9)
print t.x, t
u = t.set_x(7)
print u.x, u

tp = u.previous()
print tp.x, tp
up = tp.next()
print up.x, up