import copy

from PIL import Image

import utils


RECURSION_LIMIT = 50


class Immutable:
    
    @staticmethod
    def mutates(function):
        """
        decorator for first duplicating
        """
        def inner_function(old, *args, **kwargs):
            new = copy.copy(old)
            
            # lets do this... attach self to out as predecessor
            if hasattr(new, 'previous'):
                new.previous = old
            
            retval = function(new, *args, **kwargs)
            if not retval:
                return new
            else:
                return retval #trusting them...
            
        return inner_function
        

class DBNProcedureSet(Immutable):
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
    
    @Immutable.mutates
    def add(self, command_name, proc):
        self.dispatch[command_name] = proc

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
        
        # id like to just call this, but it halves our usable stack depth!
        #new.parent = copy.copy(self.parent)
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
    
    def __setitem__(self, key, value):
        self._inner[key] = value
        
    def __delitem__(self, key):
        del self._inner[key]
        
    def push(self):
        new_parent = copy.copy(self)
        new = DBNEnvironment(parent=new_parent)
        return new
        
    def pop(self):
        if self.parent is None:
            raise ValueError("Cannot pop an environment without a parent!")
        else:
            return copy.copy(self.parent)
        
        

class DBNInterpreterState(Immutable):
    """
    The state of the interpreter.
    Really, just the pen color, master environment?
    and, of course, the image.
    
    fucking immutable!
    """        
    
    def __init__(self, create=True):
        self.previous = None
        if create:
            self.image = DBNImage(color=255)
            self.pen_color = 0
            self.env = DBNEnvironment()
            self.commands = DBNProcedureSet()
            
            self.stack_depth = 0
                    
    def __copy__(self):
        new = DBNInterpreterState(create=False)
        
        # copy all the attributes over
        # this should be sufficient for now
        new.image = copy.copy(self.image)
        new.pen_color = self.pen_color # an integer, so no need to copy
        new.env = copy.copy(self.env)
        new.commands = copy.copy(self.commands)
        
        new.stack_depth = self.stack_depth
        
        return new
        
    def lookup_command(self, name):
        return self.commands.get(name)
        
    @Immutable.mutates
    def add_command(self, name, proc):
        self.commands = self.commands.add(name, proc)
        
    def lookup_variable(self, var):
        return self.env.get(var, 0)
     
    @Immutable.mutates
    def set_variable(self, var, to):
        self.env[var] = to
    
    @Immutable.mutates  
    def set_variables(self, **kwargs):
        for var, to in kwargs.items():
            self.env[var] = to
    
    @Immutable.mutates 
    def set(self, lval, rval):
        """
        sets lval to rval
        
        lval can be a DBNDot or a DBNVariable
        """     
        if isinstance(lval, utils.DBNDot):
            x_coord = utils.pixel_to_coord(lval.x, 'x')
            y_coord = utils.pixel_to_coord(lval.y, 'y')
            color = utils.scale_100(rval)
            self.image = self.image.set_pixel(x_coord, y_coord, color)

        elif isinstance(lval, utils.DBNVariable):
            self.env[lval.name] = rval
        
        else:
            raise ValueError("Unknown lvalue! %s" % str(lval))

    @Immutable.mutates
    def push(self):
        if self.stack_depth >= RECURSION_LIMIT:
            raise ValueError("Recursion too deep! %d" % self.stack_depth)
        else:
            self.env = self.env.push()
            self.stack_depth += 1
        
    @Immutable.mutates
    def pop(self):
        self.env = self.env.pop()
        self.stack_depth -= 1
             

class DBNImage(Immutable):
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
    
    @Immutable.mutates
    def set_pixel(self, x, y, value):
        self.__set_pixel(x, y, value)
        
    @Immutable.mutates
    def set_pixels(self, pixel_iterator):
        for x, y, value in pixel_iterator:
            self.__set_pixel(x, y, value)

import builtins