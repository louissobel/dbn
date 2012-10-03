

def scale_100(val):
    #takes the value given, between 0 - 100,
    # and scales it from 0 - 255
    return 255 - int(val * (255.0/100))
    

def pixel_to_coord(pixel, direction):
    if direction == 'x':
        return pixel
    elif direction == 'y':
        return 100 - pixel
    else:
        raise ValueError("bad direction to pixel_to_coord: %s" % direction)

class DBNVariable:
    def __init__(self, name):
        self.name = name
            
class DBNDot:
    def __init__(self, x, y):
        self.x = x
        self.y = y