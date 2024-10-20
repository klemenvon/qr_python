from PIL import Image, ImageDraw, ImageFont
from random import random

from .utils import get_alignment_pattern_positions

class GridImage():
    """
    A class for creating images from a grid of modules
    """
    default_mapping = {
        True: 'black',
        False: 'white',
        None: 'white',
        0: 'white',
        1: 'black',
        2: 'red',
        3: 'purple',
        4: 'blue',
        5: 'green',
        6: 'yellow',
        7: 'orange',
        8: 'pink',
        9: 'brown',
        10: 'grey',
    }
    def __init__(self, grid, module_size=1, **kwargs):
        self.grid = grid
        self.module_size = module_size
        self.mapping = kwargs.get('mapping', GridImage.default_mapping)
        self._validate_grid()
        self.image = self._create_image()
    
    def _validate_grid(self):
        # Check if the grid is a square
        size = len(self.grid)
        for row in self.grid:
            if len(row) != size:
                raise ValueError('Grid is not a square')
    
    def _create_image(self):
        # Creates a PIL image
        width = height = (self.module_size * len(self.grid))
        image = Image.new('RGB', (width,height))
        draw = ImageDraw.Draw(image)
        # Iterate through the grid
        for row_idx, row in enumerate(self.grid):
            for col_idx, value in enumerate(row):
                x = col_idx * self.module_size
                y = row_idx * self.module_size
                # Get color for mapping
                color = self.mapping.get(value)
                if color:
                    draw.rectangle([x, y, x + self.module_size, y + self.module_size], fill=color)
                elif isinstance(value, str):
                    draw.text((x, y), value, fill='white')
                elif isinstance(value,tuple):
                    text, color = value
                    color = self.mapping.get(color)
                    draw.rectangle([x, y, x + self.module_size, y + self.module_size], fill=color)
                    draw.text((x, y), text, fill='black')
        return image

    def save(self, filename):
        self.image.save(filename)
    
    def show(self):
        self.image.show()

class QRGenerator:
    def __init__(self, data=None, version=1, **kwargs):
        self.version = version
        self.data = data
        self.modules = None
        self.data_mask = None
        self.padding = kwargs.get('padding',4)
        self.padding_flag = False
        self.module_size = kwargs.get('module_size',1)
        self.size = None
    
    def show_mask(self):
        if self.data_mask is None:
            self._create_data_mask()
        image = GridImage(self.data_mask, self.module_size, {True: 'white', False: 'grey'})
        image.show()
    
    def save_mask(self, filename):
        if self.data_mask is None:
            self._create_data_mask()
        image = GridImage(self.data_mask, self.module_size, {True: 'white', False: 'grey'})
        image.save(filename)
    
    def _create_data_mask(self):
        print('Creating data mask')
        self.data_mask = [row[:] for row in self.modules] # Copy the modules
        for i, row in enumerate(self.data_mask):
            for j, item in enumerate(row):
                if item is not None:
                    self.data_mask[i][j] = False
                else:
                    self.data_mask[i][j] = True
    
    def show(self):
        self._add_dead_zones()
        image = self.create_image()
        image.show()
    
    def save(self, filename):
        self._add_dead_zones()
        image = self.create_image()
        image.save(filename)
    
    def _create_module_grid(self):
        """
        Filling the modules with 'False' so that we can easily tell what's been modified by the finder patterns and such.
        """
        self.size = self._size_from_version(self.version)
        self.modules = [[None for _ in range(self.size)] for _ in range(self.size)]
    
    def _add_dead_zones(self):
        if self.padding == 0 or self.padding_flag:
            return
        size_with_padding = self.size + (2 * self.padding)
        for column in self.modules:
            for _ in range(self.padding):
                column.insert(0,0)
                column.append(0)
        for _ in range(self.padding):
            self.modules.insert(0,[0 for _ in range(size_with_padding)])
            self.modules.append([0 for _ in range(size_with_padding)])
        self.padding_flag = True
    
    def add_required_elements(self):
        if self.modules is None:
            self._create_module_grid()
        self._place_all_separators()
        self._place_all_finders()
        self._place_alignment_patterns()
        self._place_timing_pattern()
        self._place_black_module()
        self._place_version_info()
        self._place_error_correction_bits()
    
    def _generate_color_data(self, size=4000):
        encoded = []
        for i in range(size):
            symbol = i % 6 + 4
            encoded.extend([symbol] * 8)
        return encoded

    def _generate_numbered_data(self, size=32000):
        encoded = []
        for i in range(size):
            encoded.append(f"{i:04d}")
        return encoded

    def _generate_debug_combo(self):
        numbers = self._generate_numbered_data()
        colors = self._generate_color_data()
        combo = []
        for num, col in zip(numbers, colors):
            combo.append((num,col))
        return combo
    
    def _encode_data(self):
        # Currently we don't take data in so generate bogus bits
        return self._generate_color_data()
    
    def _get_indexed_array(self):
        indexed = [[(i,j) for j in range(self.size)] for i in range(self.size)]
        return indexed
    
    def place_data(self):
        encoded_data = self._encode_data()
        indexed = self._get_indexed_array()
        # Throw out column 6
        indexed = indexed[:6] + indexed[7:]
        # Take the last two columns, and interleave them
        # They have to be interleaved in a pattern that goes up and then down again
        # To gain an intuition for why the lists and final flat list are flipped every other time
        # draw it out for yourself
        counter = 0
        while len(indexed) > 1:
            first = indexed.pop(-1)
            second = indexed.pop(-1)
            # Optionally reverse the lists
            flat = []
            for i, j in zip(first, second):
                # Every second pair, we need to interleave them the other way around
                if counter % 2 == 0:
                    flat.extend([j,i])
                else:
                    flat.extend([i,j])
            # Every second pair of rows, reverse the flat order as we go downwards
            if counter % 2 == 0:
                flat = flat[::-1]
            for (x,y) in flat:
                if self.modules[y][x] is None:
                    self.modules[y][x] = encoded_data.pop(0)
            counter += 1
    
    def _place_black_module(self):
        # Place a black module at the bottom right
        self.modules[self.size-8][8] = 1
    
    def _place_single_finder_pattern(self, startx=0, endx=7, starty=0, endy=7):
        for i, x in enumerate(range(startx,endx)):
            for j, y in enumerate(range(starty,endy)):
                if (i == 0 or j == 0) or (5 > j > 1 and 5 > i > 1) or (i == 6 or j == 6):
                    self.modules[x][y] = 1
                else:
                    self.modules[x][y] = 0
    
    def _place_all_finders(self):
        # Place the finder patterns
        # Top left
        self._place_single_finder_pattern()
        # Top right
        self._place_single_finder_pattern(self.size-7,self.size)
        # Bottom left
        self._place_single_finder_pattern(0,7,self.size-7,self.size)
    
    def _place_single_separator(self, startx=0, endx=8, starty=0, endy=8):
        for i in range(startx,endx):
            for j in range(starty,endy):
                self.modules[i][j] = 0
    
    def _place_all_separators(self):
        # Top left
        self._place_single_separator()

        # Top right
        self._place_single_separator(self.size-8,self.size)

        # Bottom left
        self._place_single_separator(0,8,self.size-8,self.size)
    
    def _place_timing_pattern(self):
        for i in range(8,self.size-8):
            if i % 2 == 0:
                self.modules[i][6] = 1
                self.modules[6][i] = 1
            else:
                self.modules[i][6] = 0
                self.modules[6][i] = 0
    
    def _place_alignment_patterns(self):
        positions = get_alignment_pattern_positions(self.version)
        for (x, y) in positions:
            self._place_single_alignment_pattern(x, y)
    
    def _place_single_alignment_pattern(self, xpos, ypos):
        # Place alignment pattern at centre x,y
        # First check that we don't intersect other patterns
        for i in range(xpos-2,xpos+3):
            for j in range(ypos-2,ypos+3):
                if self.modules[i][j] is not None:
                    return False
        # Place 5x5 black square
        for i,x in enumerate(range(xpos-2,xpos+3)):
            for j,y in enumerate(range(ypos-2,ypos+3)):
                if (i == 1 or i == 3) and ( 0 < j < 4) or (j == 1 or j == 3) and (0 < i < 4):
                    self.modules[x][y] = 0
                else:
                    self.modules[x][y] = 1
    
    def _place_version_info(self):
        if self.version < 7:
            return
        # Place version info
        # Bottom Left
        for x in range(6):
            for ymod in range(3):
                self.modules[self.size-11+ymod][x] = 3
        
        # Top Right
        for y in range(6):
            for xmod in range(3):
                self.modules[y][self.size-11+xmod] = 3

    def _place_error_correction_bits(self):
        # It's handy if we do this in the correct order already
        # Top left
        x = 8
        y = 0
        while y < 8:
            current = self.modules[x][y]
            if current is None:
                self.modules[x][y] = 2
            y += 1
        while x > -1:
            current = self.modules[x][y]
            if current is None:
                self.modules[x][y] = 2
            x -= 1

        # Top right
        x = 8
        y = self.size - 8
        while y < self.size:
            current = self.modules[x][y]
            if current is None:
                self.modules[x][y] = 2
            y += 1
        
        # Bottom left
        x = self.size - 7
        y = 8
        while x < self.size:
            current = self.modules[x][y]
            if current is None:
                self.modules[x][y] = 2
            x += 1

    def create_image(self):
        return GridImage(self.modules, self.module_size)
 
    @staticmethod
    def _size_from_version(version):
        return 17 + (4 * version)


