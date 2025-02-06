# String serves as our lookup table
ALPHANUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

# Base Encoder Class to avoid duplicate code
class BaseEncoder:
    def __init__(self, data):
        self.data = data
        self.mode_indicator = self._create_mode_indicator()
        self.data_blocks = self._create_data_blocks()
        self.data_length = len(str(data))   # Lenght as a string otherwise numbers don't work
        self.length_bits = None
    
    def test_length(self, qr_version):
        return 4 + len(self.data_blocks) + self._size_from_version(qr_version)
    
    def _size_from_version(self, qr_version):
        if qr_version <= 9:
            return self.SMALL
        elif qr_version <= 26:
            return self.MEDIUM
        else:
            return self.LARGE

    def encode(self, qr_version=1):
        self._create_data_blocks()
        self._create_length_bits(qr_version)
        final_stream = BitStream.merge_bitstreams([self.mode_indicator, self.length_bits, self.data_blocks])
        return final_stream
    
    def get_encoded_data(self):
        # Mostly for debugging
        return self.data_blocks
    
    def _create_mode_indicator(self):
        stream = BitStream()
        stream.put(self.MODE, 4)
        return stream
    
    def _create_data_blocks(self):
        raise NotImplementedError
    
    def _create_length_bits(self, qr_version):
        self.length_bits = BitStream()
        if qr_version <= 9:
            self.length_bits.put(self.data_length, self.SMALL)
        elif qr_version <= 26:
            self.length_bits.put(self.data_length, self.MEDIUM)
        else:
            self.length_bits.put(self.data_length, self.LARGE)

class AlphanumericEncoder(BaseEncoder):
    SMALL = 9
    MEDIUM = 11
    LARGE = 13
    MODE = 2

    def _create_data_blocks(self):
        stream = BitStream()
        for i in range(0, self.data_length, 2):
            index1 = ALPHANUM.index(self.data[i])
            index2 = ALPHANUM.index(self.data[i+1]) if i+1 < self.data_length else 0
            stream.put(index1 * 45 + index2, 11)
        return stream
    
class NumericEncoder(BaseEncoder):
    SMALL = 10
    MEDIUM = 12
    LARGE = 14
    MODE = 1

    def _create_data_blocks(self):
        stream = BitStream()
        string_data = str(self.data)
        for i in range(0, self.data_length, 3):
            # Ezpz in python because it doesn't encode it with a leading zero in bits
            num = int(string_data[i:i+3])
            stream.put(num, 10)
        return stream

class ByteEncoder(BaseEncoder):
    SMALL = 8
    MEDIUM = 16
    LARGE = 16
    MODE = 4

    def _create_data_blocks(self):
        # Just use utf-8 encoding
        stream = BitStream()
        utf8_bytes = self.data.encode('utf-8')
        for byte in utf8_bytes:
            stream.put(byte, 8)
        return stream

class BitStream:
    PADDING = [0xEC, 0x11]

    def __init__(self):
        self.buffer = []
        self.length = 0

    def __repr__(self):
        # This is just for debugging see what numbers come out
        return ".".join([str(n) for n in self.buffer])
    
    def get(self, index):
        # Never really used
        buf_index = index // 8
        return ((self.buffer[buf_index] >> (7 - index % 8)) & 1) == 1

    def put(self, num, length):
        # Puts the lenght of bits from number into our sequence
        for i in range(length):
            # Take the bit at index i from our number and insert it
            # put_bit takes boolean values only so convert a bit in position i to bool
            self.put_bit(((num >> (length - i - 1)) & 1) == 1)

    def __len__(self):
        return self.length

    def put_bit(self, bit):
        buf_index = self.length // 8
        if len(self.buffer) <= buf_index:
            self.buffer.append(0)
        if bit:     # If bit is 'True' insert it at the next position, else skip
            self.buffer[buf_index] |= 0x80 >> (self.length % 8)
        self.length += 1

    def extend(self, other):
        # Add the bits from another bit stream to this one
        for i in range(len(other)):
            self.put_bit(other.get(i))
    
    def _add_terminator_bits(self):
        """Terminator bits always 0000"""
        for _ in range(min(4, (8 - (self.length % 8)))):
            self.put_bit(False)
    
    def _pad_codewords(self, num_codewords):
        for i in range(num_codewords):
            self.put(BitStream.PADDING[i % 2], 8)
    
    def pad_to_length(self, length):
        # Add terminator bits and pad the codewords
        self._add_terminator_bits()
        self._pad_codewords((length - self.length) // 8)
    
    def to_bool_array(self):
        # Convert the buffer to an array of booleans
        return [self.get(i) for i in range(self.length)]

    @staticmethod
    def merge_bitstreams(streams):
        # Merge multiple bitstreams into one
        final_stream = BitStream()
        for stream in streams:
            final_stream.extend(stream)
        return final_stream
    
    @staticmethod
    def from_int8_array(array):
        # Convert an array of integers to a bitstream
        stream = BitStream()
        for byte in array:
            stream.put(byte, 8)
        return stream
