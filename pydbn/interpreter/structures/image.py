from PIL import Image

import interpreter.utils as utils

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
        
        x = utils.pixel_to_coord(x, 'x')
        y = utils.pixel_to_coord(y, 'y')
        
        self._image_array[x, y] = utils.scale_100(value)
        return True
        
    def set_pixels(self, pixel_iterator):
        for x, y, value in pixel_iterator:
            self.set_pixel(x, y, value)
    
    def repaper(self, color):
        color_255 = utils.scale_100(color)
        self._image = Image.new('L', (101, 101), color_255)
        self._image_array = self._image.load()
