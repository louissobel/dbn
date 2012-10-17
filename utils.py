

def clip(val, lower, upper):
    if val > upper:
        return upper
    
    if val < lower:
        return lower
        
    return val
    
def clip_255(val):
    return clip(val, 0, 255)

def scale_100(val):
    #takes the value given, between 0 - 100,
    # and scales it from 0 - 255
    scaled_val = 255 - int(val * (255.0/100))
    return clip_255(scaled_val)

def pixel_to_coord(pixel, direction):
    if direction == 'x':
        return pixel
    elif direction == 'y':
        return 100 - pixel
    else:
        raise ValueError("bad direction to pixel_to_coord: %s" % direction)


def bresenham_line(x0, y0, x1, y1):
    #http://stackoverflow.com/questions/2734714/modifying-bresenhams-line-algorithm
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0  
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    if y0 < y1: 
        ystep = 1
    else:
        ystep = -1

    deltax = x1 - x0
    deltay = abs(y1 - y0)
    error = -deltax / 2
    y = y0
   
    for x in range(x0, x1 + 1):
        if steep:
            yield (y,x)
        else:
            yield (x,y)

        error = error + deltay
        if error > 0:
            y = y + ystep
            error = error - deltax
    raise StopIteration