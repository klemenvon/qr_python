from PIL import Image, ImageDraw


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