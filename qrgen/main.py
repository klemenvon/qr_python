from typing import Union, List

from .utils import get_alignment_pattern_positions, interleave_blocks
from .encoders import BitStream, ByteEncoder
from .grid_image import GridImage
from .mask_patterns import apply_mask, evaluate_mask
from .reedsolomon import get_codeword_capacity, QRErrorCorrection
from .metadata import QRFormatInfo, QRVersionInfo

# TODO: This class seems way too big. Should refactor
class QRGenerator:
    def __init__(self,
                 data: Union[str, List[BitStream]] = None,
                 version: int = 1,
                 ec_level: str = 'L',
                 **kwargs):
        self.version = version
        self.data = data
        self.ec_level = ec_level
        self.modules = None
        self.data_mask = None
        self.mask_pattern = None
        self.padding = kwargs.get('padding',4)
        self.padding_flag = False
        self.module_size = kwargs.get('module_size',1)
        self.size = None
    
    def _pre_process_data(self):
        encoder = ByteEncoder(self.data)
        encoded_data = encoder.encode(qr_version=self.version)
        capacity = get_codeword_capacity(self.version, self.ec_level) * 8
        if len(encoded_data) > capacity:
            raise ValueError(f'Data too long for version {self.version} with error correction level {self.ec_level}')
        if capacity > len(encoded_data):
            if float(len(encoded_data)) / capacity < 0.75:
                print('Warning: Data is less than 75% the capacity of the QR code, consider using a smaller version')
        encoded_data.pad_to_length(capacity)
        return encoded_data
    
    def _prepare_data(self, encoded_data):
        qr_ec = QRErrorCorrection(version=self.version, ec_level=self.ec_level)
        rs_config = QRErrorCorrection.get_raw_block_config(self.version, self.ec_level)
        data_blocks, ec_blocks = qr_ec.encode_data(encoded_data.buffer)
        data_final = interleave_blocks(data_blocks, rs_config)
        ec_final = interleave_blocks(ec_blocks, rs_config)
        data_stream = BitStream.from_int8_array(data_final)
        ec_stream = BitStream.from_int8_array(ec_final)
        full_stream = BitStream.merge_bitstreams([data_stream, ec_stream]).to_bool_array()
        return full_stream
    
    def _encode_data(self):
        if isinstance(self.data, str):
            if self.data == "test_colors":
                return self._generate_color_data()
            return self._prepare_data(self._pre_process_data())
        elif isinstance(self.data, list):
            return BitStream.merge_bitstreams(self.data).to_bool_array()
        elif isinstance(self.data, BitStream):
            return self.data.to_bool_array()
        else:
            raise ValueError('Data must be a string or list of BitStreams')
    
    def _optimal_encoding(self):
        pass
    
    def show_mask(self):
        if self.data_mask is None:
            self._create_data_mask()
        image = GridImage(self.data_mask, self.module_size, mapping={True: 'white', False: 'grey'})
        image.show()
    
    def save_mask(self, filename):
        if self.data_mask is None:
            self._create_data_mask()
        image = GridImage(self.data_mask, self.module_size, mapping={True: 'white', False: 'grey'})
        image.save(filename)
    
    def _create_data_mask(self):
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
        # self._place_version_info_color()
        self._place_version_info()
        self._place_error_correction_bits()
        self._create_data_mask()                # Create data mask before data is placed
    
    def add_metadata(self):
        self._place_format_info()
        self._place_version_info()
    
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
    
    # def _encode_data(self):
    #     # Currently we don't take data in so generate bogus bits
    #     return self._generate_color_data()
    
    def _get_indexed_array(self):
        indexed = [[(i,j) for j in range(self.size)] for i in range(self.size)]
        return indexed
    
    def fill_white(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.modules[i][j] is None:
                    self.modules[i][j] = False
    
    def apply_mask(self, pattern_number):
        apply_mask(self.modules, self.data_mask, pattern_number)

    def _evaluate_mask(self, mask_number):
        temp_modules = [row[:] for row in self.modules] # Copy the modules
        apply_mask(temp_modules, self.data_mask, mask_number)
        eval_score = evaluate_mask(temp_modules)
        return eval_score
    
    def _find_best_mask(self):
        best_score = None
        best_mask = None
        for i in range(8):
            score = self._evaluate_mask(i)
            if best_score is None or score < best_score:
                best_score = score
                best_mask = i
        return best_mask
    
    def apply_best_mask(self):
        best_mask = self._find_best_mask()
        apply_mask(self.modules, self.data_mask, best_mask)
        self.mask_pattern = best_mask
    
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
                    try:
                        # Just pad with False if we run out of data
                        self.modules[y][x] = encoded_data.pop(0)
                    except IndexError:
                        self.modules[y][x] = 0
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
    
    def _place_version_info_color(self):
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
    
    def _place_version_info(self):
        if self.version < 7:
            return
        version_bits = QRVersionInfo.get_version_bits(self.version)

        # Bottom Left
        i = 0
        for x in range(6):
            for ymod in range(3):
                self.modules[self.size-11+ymod][x] = version_bits[i]
                i += 1
        
        # Top Right
        i = 0
        for y in range(6):
            for xmod in range(3):
                self.modules[y][self.size-11+xmod] = version_bits[i]
                i += 1

    
    def _place_format_info(self):
        if self.mask_pattern is None:
            raise ValueError('Mask pattern must be set before placing format info')
        format_bits = QRFormatInfo.get_format_bits(self.ec_level, self.mask_pattern)

        # Top left
        x = 8
        y = 0
        i = 0
        while y < 8:
            current = self.modules[x][y]
            if current != 1:
                self.modules[x][y] = format_bits[i]
                i += 1
            y += 1
        while x > -1:
            current = self.modules[x][y]
            if current != 1:
                self.modules[x][y] = format_bits[i]
                i += 1
            x -= 1
        
        # Bottom left
        x = self.size - 1
        y = 8
        i = 0
        while x > self.size - 8:
            current = self.modules[x][y]
            if current != 1:
                self.modules[x][y] = format_bits[i]
                i += 1
            x -= 1
        
        # Top right
        x = 8
        y = self.size - 8
        while y < self.size:
            current = self.modules[x][y]
            if current != 1:
                self.modules[x][y] = format_bits[i]
                i += 1
            y += 1

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

        # Bottom left
        x = self.size - 1
        y = 8
        while x > self.size - 8:
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
        
    def create_image(self):
        return GridImage(self.modules, self.module_size)
 
    @staticmethod
    def _size_from_version(version):
        return 17 + (4 * version)


