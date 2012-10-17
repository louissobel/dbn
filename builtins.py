import utils

from dbnast import DBNPythonNode
from dbnstate import Immutable, DBNImage
from structures import DBNProcedure

def builtin(formals):
    def decorator(function):        
        def inner(state):
            args = [state.lookup_variable(f) for f in formals]
            return function(state, *args)
        builtin_node = DBNPythonNode(inner)
        proc_node = DBNProcedure(formals, builtin_node)
        return proc_node
    return decorator
        
@builtin(('blX', 'blY', 'trX', 'trY'))
@Immutable.mutates
def Line(state, *args):
    
    blX, blY, trX, trY = args
    
    blX = utils.pixel_to_coord(blX, 'x')
    blY = utils.pixel_to_coord(blY, 'y')
    trX = utils.pixel_to_coord(trX, 'x')
    trY = utils.pixel_to_coord(trY, 'y')
    
    points = utils.bresenham_line(blX, blY, trX, trY)
    pixel_list = ((x, y, state.pen_color) for x, y in points)
    
    state.image = state.image.set_pixels(pixel_list)

@builtin(('value',))
@Immutable.mutates
def Paper(state, value):
    color = utils.scale_100(value)
    state.image = DBNImage(color=color)

@builtin(('value',))
@Immutable.mutates
def Pen(state, value):
    color = utils.scale_100(value)
    state.pen_color = color
    
BUILTIN_PROCS = {
    'Line': Line,
    'Paper': Paper,
    'Pen': Pen,
}