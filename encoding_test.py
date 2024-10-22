# Here we'll try to encode some data from input into a sensible string of bits.

# Bit wrangling classc courtesy of Claude

# Alphanumeric QR encoding
# String serves as our lookup table
ALPHANUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"


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

    def get_final(self, qr_version):
        self._create_data_blocks()
        self._create_length_bits(qr_version)
        final_stream = BitStream()
        final_stream.extend(self.mode_indicator)
        final_stream.extend(self.length_bits)
        final_stream.extend(self.data_blocks)
        return final_stream
    
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

class AlphaNumEncoder(BaseEncoder):
    SMALL = 9
    MEDIUM = 11
    LARGE = 13

    def _create_data_blocks(self):
        stream = BitStream()
        for i in range(0, self.data_length, 2):
            index1 = ALPHANUM.index(self.data[i])
            index2 = ALPHANUM.index(self.data[i+1]) if i+1 < self.data_length else 0
            stream.put(index1 * 45 + index2, 11)
        return stream
    
class NumericEncoder:
    SMALL = 10
    MEDIUM = 12
    LARGE = 14

    def _create_data_blocks(self):
        stream = BitStream()
        string_data = str(self.data)
        for i in range(0, self.data_length, 3):
            # Ezpz in python because it doesn't encode it with a leading zero in bits
            num = int(string_data[i:i+3])
            stream.put(num, 10)
        return stream

class ByteEncoder:
    SMALL = 8
    MEDIUM = 16
    LARGE = 16

    def _create_data_blocks(self):
        # Just use utf-8 encoding
        utf8_data = int.from_bytes(str(self.data).encode('utf-8'))
        stream = BitStream()
        stream.put(utf8_data, self.data_length * 8)
        return stream

class BitStream:
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

# Test the bit buffer
buf = BitStream()   # Create bit buffer
buf.put(10,4)       # Put in a 4 bit int
buf.put(11,4)       # Put in another 4 bit int
buf.put(15,4)       # Another 4 bit int
print(buf)

firstBuf = BitStream()
firstBuf.put(10,4)

secondBuf = BitStream()
secondBuf.put(11,4)
secondBuf.put(15,4)

firstBuf.extend(secondBuf)
print(firstBuf)

# Quick test of the utf-8 encoder
stream = BitStream()
text = "Hello"
ints = int.from_bytes(text.encode('utf-8'), 'big')
stream.put(ints, 40)
print(stream)

another = BitStream()
classic = [ord(c) for c in text]
for c in classic:
    another.put(c, 8)
print(another)

# Test the bit stream
# stream = BitStream()
# stream.append_bits(0b101, 3)
# print(stream.get_bytes())
# print(stream.get_bits(3, 5))
# print(stream.position)
# stream.append_bytes(b'Hello')
# print(stream.get_bytes())
# print(stream.get_bits(3, 5))
# print(stream.position)