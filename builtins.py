import utils

from dbnast import DBNPythonNode
from dbnstate import Producer, DBNImage
from structures import DBNProcedure

def builtin(*formals):
    def decorator(function):        
        def inner(state):
            args = [state.lookup_variable(f) for f in formals]
            return function(state, *args)
        builtin_node = DBNPythonNode(inner)
        proc_node = DBNProcedure(formals, builtin_node)
        return proc_node
    return decorator
        
@builtin('blX', 'blY', 'trX', 'trY')
@Producer
def Line(old, new, *args):
    
    blX, blY, trX, trY = args
    
    blX = utils.pixel_to_coord(blX, 'x')
    blY = utils.pixel_to_coord(blY, 'y')
    trX = utils.pixel_to_coord(trX, 'x')
    trY = utils.pixel_to_coord(trY, 'y')
    
    # use list so I can reuse the iterable
    points = list(utils.bresenham_line(blX, blY, trX, trY))
    
    color = utils.scale_100(old.pen_color)
    pixel_list = ((x, y, color) for x, y in points)
    
    new.image = old.image.set_pixels(pixel_list)
    
    current_line_no = new.line_no
    new_ghosts = (old.ghosts
                .add_dimension_line(current_line_no, 1, 'horizontal', blX, blY)  # for blX
                .add_dimension_line(current_line_no, 2, 'vertical', blX, blY) # for blY
                .add_dimension_line(current_line_no, 3, 'horizontal', trX, trY) # for trX
                .add_dimension_line(current_line_no, 4, 'vertical', trX, trY) # for trY
    )
    
    ## traverse up the environments,
    ## adding these points to the ghost pointer
    new_ghosts = new_ghosts.add_points_to_callstack(new.env, 0, points)

    new.ghosts = new_ghosts

@builtin('value')
@Producer
def Paper(old, new, value):
    color = utils.scale_100(value)
    new.image = DBNImage(color=color)

@builtin('value')
@Producer
def Pen(old, new, value):
    new.pen_color = utils.clip_100(value)
    
BUILTIN_PROCS = {
    'Line': Line,
    'Paper': Paper,
    'Pen': Pen,
}