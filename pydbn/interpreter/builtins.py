from structures import DBNBuiltinCommand

class LineCommand(DBNBuiltinCommand):

    def __init__(self):
        DBNBuiltinCommand.__init__(self, 4)

    def keyword(self):
        return 'Line'

    def call(self, interpreter, blX, blY, trX, trY):

        # use list so I can reuse the iterable

        points = list(self.bresenham_line(blX, blY, trX, trY))

        color = interpreter.pen_color
        pixel_list = ((x, y, color) for x, y in points)

        interpreter.image.set_pixels(pixel_list)

    @staticmethod
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
