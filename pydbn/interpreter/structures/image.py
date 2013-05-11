from PIL import Image

class DBNImage():
    """
    Primitive wrapper around pil image

    in DBN represention
    """
    def __init__(self, color):
        self.repaper(color)

    def query_pixel(self, x, y):
        if not 0 <= x <= 100:
            return self.base_color

        if not 0 <= y <= 100:
            return self.base_color

        x = self.dbnx_to_pilx(x)
        y = self.dbny_to_pily(y)

        return self.pil_color_to_dbn_color(self._image_array[x, y])

    def set_pixel(self, x, y, value):
        if not 0 <= x <= 100:
            return False

        if not 0 <= y <= 100:
            return False

        x = self.dbnx_to_pilx(x)
        y = self.dbny_to_pily(y)

        self._image_array[x, y] = self.dbn_color_to_pil_color(value)
        return True

    def set_pixels(self, pixel_iterator):
        for x, y, value in pixel_iterator:
            self.set_pixel(x, y, value)

    def repaper(self, color):
        self.base_color = color
        pil_color = self.dbn_color_to_pil_color(color)
        self._image = Image.new('L', (101, 101), pil_color)
        self._image_array = self._image.load()

    @staticmethod
    def dbn_color_to_pil_color(dbn_color):
        """
        clips input color to [0, 100]
        color between 0 and 100 ==> 0 - 255
        """
        clipped_dbn_color = max(0, min(dbn_color, 100))
        pil_color = int(255 * (1 - clipped_dbn_color / 100.0))
        return pil_color

    @staticmethod
    def pil_color_to_dbn_color(pil_color):
        """
        clips input value to [0, 255]
        makes it a dbn color in [0, 100]
        """
        clipped_pil_color = max(0, min(pil_color, 255))
        dbn_color = int(100 * (1 - clipped_pil_color / 255.0))
        return dbn_color

    @staticmethod
    def dbnx_to_pilx(x):
        return x

    @staticmethod
    def dbny_to_pily(y):
        return 100 - y
