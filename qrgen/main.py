# Step 1 Make basic grid and draw it
from PIL import Image
from random import random

class Grid:
    def __init__(self, size, module_size=1):
        self.size = size
        self.module_size = module_size
        self._create_blank()

    def _create_blank(self):
        self.data = [[0 for i in range(self.size)] for j in range(self.size)]

    def random_noise(self):
        for x in range(self.size):
            for y in range(self.size):
                if random() < 0.3:
                    self.data[x][y] = 1

    def reset_image(self):
        self._create_blank()

    def debug_show(self):
        print(self.data)

    def _create_image(self):
        # Creates a PIL image
        width = height = self.module_size * self.size
        image = Image.new('1', (width,height))  # Binary image format
        pixels = image.load()                   # Access pixels
        for y in range(height):
            for x in range(width):
                pixels[x,y] = self.data[y][x]
        return image

    def save_image(self,filename):
        image = self._create_image()
        image.save(filename)

    def show_image(self):
        image = self._create_image()
        image.show()

class QRGenerator:
    def __init__(self, version=1):
        pass

    @staticmethod
    def _size_from_version(version):
        return 17 + (4 * version)


