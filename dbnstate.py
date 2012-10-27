import copy

from PIL import Image

import utils
from structures import DBNVariable, DBNDot

RECURSION_LIMIT = 50

            
            
def Producer(copies=None, mutates=None):
    
    # lets first fix up mutates, copies
    if copies is None:
        copies = []
    if not isinstance(copies, (tuple, list)):
        copies = [copies]

    if mutates is None:
        raise AssertionError("Mutates shouldnt' be onone,,, thats not a producer!")
    if not isinstance(mutates, (tuple, list)):
        mutates = [mutates]
    
    if len(mutates) == 0:
        raise AssertionError("mutates shouldn't be length 0, either")
    
    def decorator(function):
        
        if mutates[0] == 'self':
            def inner(old_self, *args, **kwargs):
                if 'self' in copies:
                    new_self = copy.copy(old_self)
                    args = (new_self,) + args               
                new = function(old_self, *args, **kwargs)
                return new
            return inner
        
        def inner(old, *args, **kwargs):
            new = copy.copy(old)
            
            copied_values = []
            for mutatant in mutates:
                attr = getattr(old, mutatant)
                if mutatant in copies:
                    attr = copy.copy(attr)
                    copied_values.append(attr)
                
            retval = function(*((old, ) + tuple(copied_values) + args), **kwargs)
            
            if len(mutates) > 1:
                if not isinstance(retval, tuple):
                    raise AssertionError("retval must be tuple if mutating more than one")
                if len(mutates) != len(retval):
                    raise AssertionError("return value length must be same as number of mutatants")
                
                for mutatant, new_value in zip(mutates, retval):
                    setattr(new, mutatant, new_value)
            else:
                setattr(new, mutates[0], retval)
                
            # attach forward and back links if they exist
            if hasattr(old, 'next'):
                old.next = new
            
            if hasattr(new, 'previous'):
                new.previous = old
            
            return new
        return inner
    return decorator
              


class DBNProcedureSet():
    """
    For now, just the built ins (Line, Paper, Pen)
    """
    
    def __init__(self):
        self.dispatch = {}
        self.dispatch.update(builtins.BUILTIN_PROCS)  # adds the builtins
        
    def __copy__(self):
        new = DBNProcedureSet() # because the builtins come builtin
        new.dispatch = copy.copy(self.dispatch)
        return new
    
    def get(self, command_name):
        return self.dispatch.get(command_name, None)
    
    @Producer(copies='dispatch', mutates='dispatch')
    def add(old, new_dispatch, command_name, proc):
        new_dispatch[command_name] = proc
        return new_dispatch
        
class DBNEnvironment(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self._inner = {}
    
    def __copy_without_parent(self):
        new = DBNEnvironment()
        new._inner = copy.copy(self._inner)
        return new
        
    def __copy__(self):
        new = self.__copy_without_parent()
        
        # id like to just call this, but it halves our usable stack depth (recursion)!
        # new.parent = copy.copy(self.parent)
        # so fuu... make it an iteration? thats OK, but clutters the interface
        # ! not if we use deep copy too!
        # that's probably what I should do throughout the code,
        # but for now, I'm just going to hack it.
        current_old = self
        current_new = new
        while current_old.parent is not None:
            current_new.parent = current_old.parent.__copy_without_parent()
            current_new = current_new.parent
            current_old = current_old.parent
        
        return new
    
    def __len__(self):
        return len(self._inner)
    
    def __getitem__(self, key):
        out = self.get(key)
        if out is None:
            raise KeyError("%s not found in environment heirarchy" % key)
    
    def get(self, key, default=None):
        """
        searches this first, then parents
        """
        try:
            return self._inner[key]
        except KeyError:
            if self.parent is None:
                return default
            else:
                return self.parent.get(key, default)        
    
    @Producer(copies='_inner', mutates='_inner')
    def set(old, _inner, key, value):
        _inner[key] = value
        return _inner
        
    @Producer(copies='_inner', mutates='_inner')
    def update(old, _inner, dct):
        _inner.update(dct)
        return _inner
      
    @Producer(copies='_inner', mutates='_inner') 
    def delete(old, _inner, key):
        del _inner[key]
        return _inner
    
    @Producer(copies='self', mutates='self')  
    def push(old_self, new_self):
        child = DBNEnvironment(parent=new_self)
        return child
    
    @Producer(mutates='self')
    def pop(old):
        if old.parent is None:
            raise ValueError("Cannot pop an environment without a parent!")
        else:
            return copy.copy(old.parent)
        
        

class DBNInterpreterState(object):
    """
    The state of the interpreter.
    Really, just the pen color, master environment?
    and, of course, the image.
    
    fucking immutable!
    """ 
    
    next = None
    previous = None     
    
    def __init__(self):
        self.image = DBNImage(color=255)
        self.pen_color = 0
        self.env = DBNEnvironment()
        self.commands = DBNProcedureSet()
        
        self.stack_depth = 0
        self.line_no = -1
                
    def lookup_command(self, name):
        return self.commands.get(name)
        
    @Producer(mutates='commands')
    def add_command(old, name, proc):
        return old.commands.add(name, proc)
        
    def lookup_variable(self, var):
        return self.env.get(var, 0)
     
    @Producer(mutates='env')
    def set_variable(old, var, to):
        return old.env.set(var, to)
    
    @Producer(mutates='env')
    def set_variables(old, **kwargs):
        return old.env.update(kwargs)
    
    @Producer(mutates=('image', 'env'))
    def set(old, lval, rval):
        """
        sets lval to rval
        
        lval can be a DBNDot or a DBNVariable
        """     
        if isinstance(lval, DBNDot):
            x_coord = utils.pixel_to_coord(lval.x, 'x')
            y_coord = utils.pixel_to_coord(lval.y, 'y')
            color = utils.scale_100(rval)
            return old.image.set_pixel(x_coord, y_coord, color), old.env

        elif isinstance(lval, DBNVariable):
            return old.image, old.env.set(lval.name, rval)
        
        else:
            raise ValueError("Unknown lvalue! %s" % str(lval))

    @Producer(mutates=('env', 'stack_depth'))
    def push(old):
        if old.stack_depth >= RECURSION_LIMIT:
            raise ValueError("Recursion too deep! %d" % old.stack_depth)
        else:
            return (old.env.push(), old.stack_depth + 1)
        
    @Producer(mutates=('env', 'stack_depth'))
    def pop(old):
        return (old.env.pop(), old.stack_depth - 1)
    
    @Producer(mutates='line_no')
    def set_line_no(_, line_no):
        # line_no SHOULD NEVER BE -1
        if line_no == -1:
            raise AssertionError("HOW LINE_NO -1?")
        return line_no
             

class DBNImage():
    """
    Primitive wrapper around pil image
    
    in PIL represention, not DBN (255, upper left origin, etc)
    """
    def __init__(self, color=255, create=True):
        if create:
            self._image = Image.new('L', (101, 101), color)
            self._image_array = self._image.load()
        
    def __copy__(self):
         new = DBNImage(create=False)
         new._image = self._image.copy()
         new._image_array = new._image.load()
         return new
    
    def query_pixel(self, x, y):
        return self._image_array[x, y]
    
    def __set_pixel(self, x, y, value):
        if x > 100:
            return False
        if x < 0:
            return False
        
        if y > 100:
            return False
        if y < 0:
            return False
    
        self._image_array[x, y] = value
        return True
    
    @Producer(copies='self', mutates='self')
    def set_pixel(old_self, new_self, x, y, value):
        new_self.__set_pixel(x, y, value)
        return new_self
        
    @Producer(copies='self', mutates='self')
    def set_pixels(old_self, new_self, pixel_iterator):
        for x, y, value in pixel_iterator:
            new_self.__set_pixel(x, y, value)
        return new_self

import builtins