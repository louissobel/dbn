import copy

from PIL import Image
import utils

class DBNFrame(object):
    
    def __init__(self, parent=None, base_line_no=-1, return_pointer=-1, depth=0):
        self.base_line_no = base_line_no
        self.parent = parent
        self.env = {}

        self.stack = []
        self.return_pointer = return_pointer
        
        self.depth = depth
    
    def __len__(self):
        return len(self.variables)
    
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
                return self.parent.get(key, default)        
    
    def bind_variable(self, key, value):
        self.env[key] = value
    
    def bind_variables(self, **dct):
        self.env.update(dct)

    def delete(self):
        del self.env[key]
    
    def __str__(self):
        out = str(self.env)
        if self.parent is not None:
            out = "(%s --> %s)" % (out, str(self.parent))
        return out


class DBNImage():
    """
    Primitive wrapper around pil image
    
    in DBN represention
    """
    def __init__(self, color):
        self.repaper(color)
    
    def query_pixel(self, x, y):
        return self._image_array[x, y]
    
    def set_pixel(self, x, y, value):
        if not 0 <= x <= 100:
            return False
        
        if not 0 <= y <= 100:
            return False
        
        # y needs to be flipped
        y = 100 - y
        
        self._image_array[x, y] = utils.scale_100(value)
        return True
        
    def set_pixels(self, pixel_iterator):
        for x, y, value in pixel_iterator:
            self.set_pixel(x, y, value)
    
    def repaper(self, color):
        color_255 = utils.scale_100(color)
        self._image = Image.new('L', (101, 101), color_255)
        self._image_array = self._image.load()
