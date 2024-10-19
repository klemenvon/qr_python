# Step 1 Make basic grid and draw it
from PIL import Image
from random import random

class Grid:
    def __init__(self, size, module_size=1, padding=4):
        self.size = size
        self.module_size = module_size
        self.padding = padding
        self.padding_flag = False
        self._create_blank()

    def _create_blank(self):
        self.data = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.padding_flag = False

    def random_noise(self):
        for x in range(self.size):
            for y in range(self.size):
                if random() < 0.3:
                    self.data[x][y] = 1
    
    def _add_padding(self):
        if self.padding_flag:
            return
        size_with_padding = self.size + (2 * self.padding)
        for column in self.data:
            for _ in range(self.padding):
                column.insert(0,1)
                column.append(1)
        for _ in range(self.padding):
            self.data.insert(0,[1 for _ in range(size_with_padding)])
            self.data.append([1 for _ in range(size_with_padding)])

    def reset_image(self):
        self._create_blank()

    def debug_show(self):
        print(self.data)
    
    def debug_whole(self):
        print('Size:',self.size)
        print('Module Size:',self.module_size)
        print('Padding:',self.padding)
        print('Padding Flag:',self.padding_flag)
        for i, row in enumerate(self.data):
            print(f"Row {i}: {len(row)}")
    
    def _validate_data(self):
        # Check if the data is a square
        size = len(self.data)
        print('Size:',size)
        for row in self.data:
            if len(row) != size:
                raise ValueError('Data is not a square')

    def _create_image(self):
        # Creates a PIL image
        self._validate_data()
        if self.padding > 0:
            print("Adding padding")
            self._add_padding()
        self.debug_whole()
        width = height = (self.module_size * len(self.data))
        image = Image.new('1', (width,height))  # Binary image format
        pixels = image.load()                   # Access pixels
        # Iterate through the data
        try:
            for y in range(len(self.data)):
                for x in range(len(self.data[y])):
                    for j in range(self.module_size):
                        for i in range(self.module_size):
                            pixels[(x*self.module_size)+i, (y*self.module_size)+j] = self.data[y][x]
        except IndexError:
            print('Index Error at x:',x,'y:',y)
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


