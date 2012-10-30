

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
    
def dimension_line(direction, x, y):
    """'
    yields the points for a direction line
    """ 
    L = 2 # end size in pixels (half the end size, actually)
    if direction == 'horizontal':
        x = x - 1
        l_x1 = 0
        l_y1 = y
        l_x2 = x
        l_y2 = y
        
        d1_x1 = 0
        d1_y1 = y - L
        d1_x2 = 0
        d1_y2 = y + L
        
        d2_x1 = x
        d2_y1 = y - L
        d2_x2 = x
        d2_y2 = y + L 
           
    elif direction == 'vertical':
        y = y + 1 # plus 1 because it is already transformed
        l_x1 = x
        l_y1 = pixel_to_coord(0, 'y')
        l_x2 = x
        l_y2 = y
        
        d1_x1 = x + L
        d1_y1 = pixel_to_coord(0, 'y')
        d1_x2 = x - L
        d1_y2 = pixel_to_coord(0, 'y')
        
        d2_x1 = x - L
        d2_y1 = y
        d2_x2 = x + L
        d2_y2 = y
        
    lines = [
        (l_x1, l_y1, l_x2, l_y2),
        (d1_x1, d1_y1, d1_x2, d1_y2),
        (d2_x1, d2_y1, d2_x2, d2_y2),
    ]
    
    for line_points in lines:
        for point in bresenham_line(*line_points):
            yield point
    raise StopIteration