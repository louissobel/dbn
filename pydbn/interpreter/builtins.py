import utils
from structures import DBNBuiltinCommand

class LineCommand(DBNBuiltinCommand):

    def __init__(self):
        DBNBuiltinCommand.__init__(self, 4)

    def keyword(self):
        return 'Line'

    def call(self, interpreter, blX, blY, trX, trY):

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
        
COMMANDS = [
    LineCommand,
    PaperCommand,
    PenCommand,
]
    