class QRFormatInfo:
    # Error correction level indicators (2 bits)
    EC_LEVELS = {
        'L': 0b01,  # 01
        'M': 0b00,  # 00
        'Q': 0b11,  # 11
        'H': 0b10   # 10
    }
    
    # Pre-computed format information bits
    # Key: (ec_level, mask_pattern)
    # Value: 15-bit format information with error correction
    # Note: Values are XORed with 0b101010000010010 to mask the patterns
    FORMAT_INFO = {
        # L error correction level
        ('L', 0): 0b111011111000100,
        ('L', 1): 0b111001011110011,
        ('L', 2): 0b111110110101010,
        ('L', 3): 0b111100010011101,
        ('L', 4): 0b110011000101111,
        ('L', 5): 0b110001100011000,
        ('L', 6): 0b110110001000001,
        ('L', 7): 0b110100101110110,
        
        # M error correction level
        ('M', 0): 0b101010000010010,
        ('M', 1): 0b101000100100101,
        ('M', 2): 0b101111001111100,
        ('M', 3): 0b101101101001011,
        ('M', 4): 0b100010111111001,
        ('M', 5): 0b100000011001110,
        ('M', 6): 0b100111110010111,
        ('M', 7): 0b100101010100000,
        
        # Q error correction level
        ('Q', 0): 0b011010101011111,
        ('Q', 1): 0b011000001101000,
        ('Q', 2): 0b011111100110001,
        ('Q', 3): 0b011101000000110,
        ('Q', 4): 0b010010010110100,
        ('Q', 5): 0b010000110000011,
        ('Q', 6): 0b010111011011010,
        ('Q', 7): 0b010101111101101,
        
        # H error correction level
        ('H', 0): 0b001011010001001,
        ('H', 1): 0b001001110111110,
        ('H', 2): 0b001110011100111,
        ('H', 3): 0b001100111010000,
        ('H', 4): 0b000011101100010,
        ('H', 5): 0b000001001010101,
        ('H', 6): 0b000110100001100,
        ('H', 7): 0b000100000111011
    }

    @staticmethod
    def get_format_bits(ec_level: str, mask_pattern: int) -> list[bool]:
        """
        Get the format information as a list of boolean values,
        ready for placement in the QR code matrix.
        
        Args:
            ec_level: Error correction level ('L', 'M', 'Q', or 'H')
            mask_pattern: Mask pattern number (0-7)
            
        Returns:
            List of 15 booleans representing format information bits
        """
        if ec_level not in ['L', 'M', 'Q', 'H']:
            raise ValueError("Invalid error correction level")
        if not (0 <= mask_pattern <= 7):
            raise ValueError("Invalid mask pattern")
            
        format_bits = QRFormatInfo.FORMAT_INFO[(ec_level, mask_pattern)]
        return [bit == '1' for bit in format(format_bits, '015b')]

    @staticmethod
    def decode_format_info(format_bits: int) -> tuple[str, int]:
        """
        Decode format information bits back to EC level and mask pattern.
        Useful for verification or reading QR codes.
        
        Args:
            format_bits: 15-bit integer of format information
            
        Returns:
            Tuple of (ec_level, mask_pattern)
        """
        # Reverse lookup in FORMAT_INFO
        for (ec_level, mask), bits in QRFormatInfo.FORMAT_INFO.items():
            if bits == format_bits:
                return (ec_level, mask)
        raise ValueError("Invalid format information bits")

    @staticmethod
    def extract_format_data(format_bits: int) -> dict:
        """
        Extract the raw format data before error correction.
        
        Args:
            format_bits: 15-bit integer of format information
            
        Returns:
            Dictionary with 'ec_level' and 'mask_pattern' keys
        """
        # XOR with the mask pattern to get original data
        data = format_bits ^ 0b101010000010010
        
        # First 2 bits are EC level
        ec_bits = (data >> 13) & 0b11
        # Next 3 bits are mask pattern
        mask = (data >> 10) & 0b111
        
        # Convert EC bits back to letter
        ec_level = next(k for k, v in QRFormatInfo.EC_LEVELS.items() 
                       if v == ec_bits)
        
        return {
            'ec_level': ec_level,
            'mask_pattern': mask
        }


class QRVersionInfo:
    # Pre-computed version information bits
    # Format: version_number: (version_info_bits1, version_info_bits2)
    # Each value is an 18-bit number where:
    # - Bits 0-5: Version number (6 bits)
    # - Bits 6-17: Error correction bits (12 bits)
    VERSION_INFO = {
        7:  (0b000111110010010100, 0b000111110010010100),
        8:  (0b001000010110111100, 0b001000010110111100),
        9:  (0b001001101010011001, 0b001001101010011001),
        10: (0b001010010011010011, 0b001010010011010011),
        11: (0b001011101111110110, 0b001011101111110110),
        12: (0b001100011101100010, 0b001100011101100010),
        13: (0b001101100001000111, 0b001101100001000111),
        14: (0b001110011000001101, 0b001110011000001101),
        15: (0b001111100100101000, 0b001111100100101000),
        16: (0b010000101101111000, 0b010000101101111000),
        17: (0b010001010001011101, 0b010001010001011101),
        18: (0b010010101000010111, 0b010010101000010111),
        19: (0b010011010100110010, 0b010011010100110010),
        20: (0b010100100110100110, 0b010100100110100110),
        21: (0b010101011010000011, 0b010101011010000011),
        22: (0b010110100011001001, 0b010110100011001001),
        23: (0b010111011111101100, 0b010111011111101100),
        24: (0b011000111011000100, 0b011000111011000100),
        25: (0b011001000111100001, 0b011001000111100001),
        26: (0b011010111110101011, 0b011010111110101011),
        27: (0b011011000010001110, 0b011011000010001110),
        28: (0b011100110000011010, 0b011100110000011010),
        29: (0b011101001100111111, 0b011101001100111111),
        30: (0b011110110101110101, 0b011110110101110101),
        31: (0b011111001001010000, 0b011111001001010000),
        32: (0b100000100111010101, 0b100000100111010101),
        33: (0b100001011011110000, 0b100001011011110000),
        34: (0b100010100010111010, 0b100010100010111010),
        35: (0b100011011110011111, 0b100011011110011111),
        36: (0b100100101100001011, 0b100100101100001011),
        37: (0b100101010000101110, 0b100101010000101110),
        38: (0b100110101001100100, 0b100110101001100100),
        39: (0b100111010101000001, 0b100111010101000001),
        40: (0b101000110001101001, 0b101000110001101001)
    }

    @staticmethod
    def get_version_info(version: int) -> tuple[int, int]:
        """
        Get the version information bits for a specific QR code version.
        Returns a tuple of two 18-bit integers for versions 7 and up,
        or (None, None) for versions 1-6 which don't need version info.
        
        Args:
            version: QR code version (1-40)
            
        Returns:
            Tuple of (version_info1, version_info2) or (None, None) for versions 1-6
        """
        if version < 7:
            return (None, None)
        if version > 40:
            raise ValueError("Invalid QR code version")
            
        return QRVersionInfo.VERSION_INFO[version]

    @staticmethod
    def get_version_bits(version: int) -> list[bool]:
        """
        Get the version information as a list of boolean values,
        ready for placement in the QR code matrix.
        
        Args:
            version: QR code version (1-40)
            
        Returns:
            List of 18 booleans or None for versions 1-6
        """
        info = QRVersionInfo.get_version_info(version)
        if info[0] is None:
            return None
            
        # Convert to binary and pad to 18 bits
        bits = format(info[0], '018b')
        return [bit == '1' for bit in bits]
