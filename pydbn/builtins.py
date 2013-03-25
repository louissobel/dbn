import utils

from structures import DBNBuiltinCommand

class LineCommand(DBNBuiltinCommand):
    
    def __init__(self):
        DBNBuiltinCommand.__init__(self, 4)
    
    def keyword(self):
        return 'Line'
    
    def call(self, interpreter, blX, blY, trX, trY):
    
        blX = utils.pixel_to_coord(blX, 'x')
        blY = utils.pixel_to_coord(blY, 'y')
        trX = utils.pixel_to_coord(trX, 'x')
        trY = utils.pixel_to_coord(trY, 'y')
    
        # use list so I can reuse the iterable
        points = list(utils.bresenham_line(blX, blY, trX, trY))
    
        color = interpreter.pen_color
        pixel_list = ((x, y, color) for x, y in points)
    
        interpreter.image.set_pixels(pixel_list)

class PaperCommand(DBNBuiltinCommand):

    def __init__(self):
        DBNBuiltinCommand.__init__(self, 1)
    
    def keyword(self):
        return 'Paper'
    
    def call(self, interpreter, color):
        interpreter.image.repaper(color)

class PenCommand(DBNBuiltinCommand):
    
    def __init__(self):
        DBNBuiltinCommand.__init__(self, 1)
    
    def keyword(self):
        return 'Pen'
    
    def call(self, interpreter, color):
        interpreter.pen_color = color
        
BUILTIN_COMMANDS = [
    LineCommand,
    PaperCommand,
    PenCommand,
]

def load_builtins(interpreter):
    for command_klass in BUILTIN_COMMANDS:
        command = command_klass()
        interpreter.commands[command.keyword()] = command
    