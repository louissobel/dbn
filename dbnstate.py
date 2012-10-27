import copy

from PIL import Image

import utils
from structures import DBNVariable, DBNDot

RECURSION_LIMIT = 50

            
            
 
def Producer(function): 
    def inner(old, *args, **kwargs):
        new = copy.copy(old)
            
        retval = function(*((old, new) + args), **kwargs)
            
        if retval is new or retval is None:
            pass
        else:
            raise AssertionError("must return new instance from Producer method")
            
        # attach forward and back links if they exist
        if hasattr(old, 'next'):
            old.next = new
        
        if hasattr(new, 'previous'):
            new.previous = old
        
        return new
    return inner

              


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
    
    @Producer
    def add(old, new, command_name, proc):
        new.dispatch[command_name] = proc
        
class DBNEnvironment(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self._inner = {}

    def __copy__(self):
        new = DBNEnvironment(parent=self.parent)
        new._inner = copy.copy(self._inner)
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
    
    @Producer
    def set(old, new, key, value):
        new._inner[key] = value
        
    @Producer
    def update(old, new, dct):
        new._inner.update(dct)
      
    @Producer
    def delete(old, new, key):
        del new._inner[key]
      
    def push(self):
        child = DBNEnvironment(parent=self)
        return child
    
    def pop(self):
        if self.parent is None:
            raise ValueError("Cannot pop an environment without a parent!")
        else:
            return self.parent
        
        
class DBNInterpreterState(object):
    """
    The state of the interpreter.
    Really, just the pen color, master environment?
    and, of course, the image.
    
    fucking immutable!
    """ 
    
    next = None
    previous = None     
    
    def __init__(self, new=True):
        if new:
            self.image = DBNImage(color=255)
            self.pen_color = 0
            self.env = DBNEnvironment()
            self.commands = DBNProcedureSet()
        
            self.stack_depth = 0
            self.line_no = -1
    
    def __copy__(self):
        new = DBNInterpreterState(new=False)

        new.image = self.image
        new.pen_color = self.pen_color
        new.env = self.env
        new.commands = self.commands
        
        new.stack_depth = self.stack_depth
        new.line_no = self.line_no
        
        return new
        
      
    def lookup_command(self, name):
        return self.commands.get(name)
        
    @Producer
    def add_command(old, new, name, proc):
        new.commands = old.commands.add(name, proc)
        
    def lookup_variable(self, var):
        return self.env.get(var, 0)
     
    @Producer
    def set_variable(old, new, var, to):
        new.env = old.env.set(var, to)
    
    @Producer
    def set_variables(old, new, **kwargs):
        new.env = old.env.update(kwargs)
    
    @Producer
    def set(old, new, lval, rval):
        """
        sets lval to rval
        
        lval can be a DBNDot or a DBNVariable
        """     
        if isinstance(lval, DBNDot):
            x_coord = utils.pixel_to_coord(lval.x, 'x')
            y_coord = utils.pixel_to_coord(lval.y, 'y')
            color = utils.scale_100(rval)
            new.image = old.image.set_pixel(x_coord, y_coord, color)

        elif isinstance(lval, DBNVariable):
            new.env = old.env.set(lval.name, rval)
        
        else:
            raise ValueError("Unknown lvalue! %s" % str(lval))

    @Producer
    def push(old, new):
        if old.stack_depth >= RECURSION_LIMIT:
            raise ValueError("Recursion too deep! %d" % old.stack_depth)
        else:
            new.env = old.env.push()
            new.stack_depth = old.stack_depth + 1
        
    @Producer
    def pop(old, new):
        new.env = old.env.pop()
        new.stack_depth = old.stack_depth - 1
    
    @Producer
    def set_line_no(old, new, line_no):
        # line_no SHOULD NEVER BE -1
        if line_no == -1:
            raise AssertionError("HOW LINE_NO -1?")
        new.line_no = 1
             

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
    
    @Producer
    def set_pixel(old, new, x, y, value):
        new.__set_pixel(x, y, value)
        return new
        
    @Producer
    def set_pixels(old, new, pixel_iterator):
        for x, y, value in pixel_iterator:
            new.__set_pixel(x, y, value)
        return new

import builtins