# This is gonna be the toughest bit of this project I think
from typing import List, Tuple
from dataclasses import dataclass
from .polynomial_gen import GeneratorPolynomialCalculator

"""
Blocks defined here are as follows:
(1, 26, 19) means 1 block of 26 total codewords with 19 data codewords
Even though our Reed-Solomon strategy with Modulo 256 could support code blocks of 255 codewords,
the cap is 152 codewords per data block for QR Codes.

Each version of the QR code has 4 entries for each of the different levels of error correction.
L - Low
M - Medium
Q - Quartile
H - High
"""
RS_BLOCK_TABLE = (
    # L
    # M
    # Q
    # H
    # 1
    (1, 26, 19),
    (1, 26, 16),
    (1, 26, 13),
    (1, 26, 9),
    # 2
    (1, 44, 34),
    (1, 44, 28),
    (1, 44, 22),
    (1, 44, 16),
    # 3
    (1, 70, 55),
    (1, 70, 44),
    (2, 35, 17),
    (2, 35, 13),
    # 4
    (1, 100, 80),
    (2, 50, 32),
    (2, 50, 24),
    (4, 25, 9),
    # 5
    (1, 134, 108),
    (2, 67, 43),
    (2, 33, 15, 2, 34, 16),
    (2, 33, 11, 2, 34, 12),
    # 6
    (2, 86, 68),
    (4, 43, 27),
    (4, 43, 19),
    (4, 43, 15),
    # 7
    (2, 98, 78),
    (4, 49, 31),
    (2, 32, 14, 4, 33, 15),
    (4, 39, 13, 1, 40, 14),
    # 8
    (2, 121, 97),
    (2, 60, 38, 2, 61, 39),
    (4, 40, 18, 2, 41, 19),
    (4, 40, 14, 2, 41, 15),
    # 9
    (2, 146, 116),
    (3, 58, 36, 2, 59, 37),
    (4, 36, 16, 4, 37, 17),
    (4, 36, 12, 4, 37, 13),
    # 10
    (2, 86, 68, 2, 87, 69),
    (4, 69, 43, 1, 70, 44),
    (6, 43, 19, 2, 44, 20),
    (6, 43, 15, 2, 44, 16),
    # 11
    (4, 101, 81),
    (1, 80, 50, 4, 81, 51),
    (4, 50, 22, 4, 51, 23),
    (3, 36, 12, 8, 37, 13),
    # 12
    (2, 116, 92, 2, 117, 93),
    (6, 58, 36, 2, 59, 37),
    (4, 46, 20, 6, 47, 21),
    (7, 42, 14, 4, 43, 15),
    # 13
    (4, 133, 107),
    (8, 59, 37, 1, 60, 38),
    (8, 44, 20, 4, 45, 21),
    (12, 33, 11, 4, 34, 12),
    # 14
    (3, 145, 115, 1, 146, 116),
    (4, 64, 40, 5, 65, 41),
    (11, 36, 16, 5, 37, 17),
    (11, 36, 12, 5, 37, 13),
    # 15
    (5, 109, 87, 1, 110, 88),
    (5, 65, 41, 5, 66, 42),
    (5, 54, 24, 7, 55, 25),
    (11, 36, 12, 7, 37, 13),
    # 16
    (5, 122, 98, 1, 123, 99),
    (7, 73, 45, 3, 74, 46),
    (15, 43, 19, 2, 44, 20),
    (3, 45, 15, 13, 46, 16),
    # 17
    (1, 135, 107, 5, 136, 108),
    (10, 74, 46, 1, 75, 47),
    (1, 50, 22, 15, 51, 23),
    (2, 42, 14, 17, 43, 15),
    # 18
    (5, 150, 120, 1, 151, 121),
    (9, 69, 43, 4, 70, 44),
    (17, 50, 22, 1, 51, 23),
    (2, 42, 14, 19, 43, 15),
    # 19
    (3, 141, 113, 4, 142, 114),
    (3, 70, 44, 11, 71, 45),
    (17, 47, 21, 4, 48, 22),
    (9, 39, 13, 16, 40, 14),
    # 20
    (3, 135, 107, 5, 136, 108),
    (3, 67, 41, 13, 68, 42),
    (15, 54, 24, 5, 55, 25),
    (15, 43, 15, 10, 44, 16),
    # 21
    (4, 144, 116, 4, 145, 117),
    (17, 68, 42),
    (17, 50, 22, 6, 51, 23),
    (19, 46, 16, 6, 47, 17),
    # 22
    (2, 139, 111, 7, 140, 112),
    (17, 74, 46),
    (7, 54, 24, 16, 55, 25),
    (34, 37, 13),
    # 23
    (4, 151, 121, 5, 152, 122),
    (4, 75, 47, 14, 76, 48),
    (11, 54, 24, 14, 55, 25),
    (16, 45, 15, 14, 46, 16),
    # 24
    (6, 147, 117, 4, 148, 118),
    (6, 73, 45, 14, 74, 46),
    (11, 54, 24, 16, 55, 25),
    (30, 46, 16, 2, 47, 17),
    # 25
    (8, 132, 106, 4, 133, 107),
    (8, 75, 47, 13, 76, 48),
    (7, 54, 24, 22, 55, 25),
    (22, 45, 15, 13, 46, 16),
    # 26
    (10, 142, 114, 2, 143, 115),
    (19, 74, 46, 4, 75, 47),
    (28, 50, 22, 6, 51, 23),
    (33, 46, 16, 4, 47, 17),
    # 27
    (8, 152, 122, 4, 153, 123),
    (22, 73, 45, 3, 74, 46),
    (8, 53, 23, 26, 54, 24),
    (12, 45, 15, 28, 46, 16),
    # 28
    (3, 147, 117, 10, 148, 118),
    (3, 73, 45, 23, 74, 46),
    (4, 54, 24, 31, 55, 25),
    (11, 45, 15, 31, 46, 16),
    # 29
    (7, 146, 116, 7, 147, 117),
    (21, 73, 45, 7, 74, 46),
    (1, 53, 23, 37, 54, 24),
    (19, 45, 15, 26, 46, 16),
    # 30
    (5, 145, 115, 10, 146, 116),
    (19, 75, 47, 10, 76, 48),
    (15, 54, 24, 25, 55, 25),
    (23, 45, 15, 25, 46, 16),
    # 31
    (13, 145, 115, 3, 146, 116),
    (2, 74, 46, 29, 75, 47),
    (42, 54, 24, 1, 55, 25),
    (23, 45, 15, 28, 46, 16),
    # 32
    (17, 145, 115),
    (10, 74, 46, 23, 75, 47),
    (10, 54, 24, 35, 55, 25),
    (19, 45, 15, 35, 46, 16),
    # 33
    (17, 145, 115, 1, 146, 116),
    (14, 74, 46, 21, 75, 47),
    (29, 54, 24, 19, 55, 25),
    (11, 45, 15, 46, 46, 16),
    # 34
    (13, 145, 115, 6, 146, 116),
    (14, 74, 46, 23, 75, 47),
    (44, 54, 24, 7, 55, 25),
    (59, 46, 16, 1, 47, 17),
    # 35
    (12, 151, 121, 7, 152, 122),
    (12, 75, 47, 26, 76, 48),
    (39, 54, 24, 14, 55, 25),
    (22, 45, 15, 41, 46, 16),
    # 36
    (6, 151, 121, 14, 152, 122),
    (6, 75, 47, 34, 76, 48),
    (46, 54, 24, 10, 55, 25),
    (2, 45, 15, 64, 46, 16),
    # 37
    (17, 152, 122, 4, 153, 123),
    (29, 74, 46, 14, 75, 47),
    (49, 54, 24, 10, 55, 25),
    (24, 45, 15, 46, 46, 16),
    # 38
    (4, 152, 122, 18, 153, 123),
    (13, 74, 46, 32, 75, 47),
    (48, 54, 24, 14, 55, 25),
    (42, 45, 15, 32, 46, 16),
    # 39
    (20, 147, 117, 4, 148, 118),
    (40, 75, 47, 7, 76, 48),
    (43, 54, 24, 22, 55, 25),
    (10, 45, 15, 67, 46, 16),
    # 40
    (19, 148, 118, 6, 149, 119),
    (18, 75, 47, 31, 76, 48),
    (34, 54, 24, 34, 55, 25),
    (20, 45, 15, 61, 46, 16),
)

EC_INDEX = {
    'L': 0,
    'M': 1,
    'Q': 2,
    'H': 3,
}

def get_rs_block_table(version, ec_mode):
    if version < 1 or version > 40:
        raise ValueError('Invalid version number.')
    return RS_BLOCK_TABLE[(version - 1) * 4 + EC_INDEX[ec_mode]]

def get_codeword_capacity(version, ec_mode):
    config = get_rs_block_table(version, ec_mode)
    block_config = [config[i:i + 3] for i in range(0, len(config), 3)]
    return sum([
        data * count
        for count, _, data in block_config
    ])

class RSBlock:
    total_count: int
    data_count: int

def rs_blocks(version, ec_mode):
    info_block = get_rs_block_table(version, ec_mode)
    blocks = []
    for i in range(0, len(info_block), 3):
        blocks.append(RSBlock(*info_block[i:i + 3]))
    return blocks

@dataclass
class RSBlock:
    """Represents a Reed-Solomon block configuration"""
    total_words: int
    data_words: int
    
    @property
    def ec_words(self) -> int:
        """Number of error correction words"""
        return self.total_words - self.data_words

class ReedSolomonEncoder:
    def __init__(self, generator_calculator):
        self.generator_calc = generator_calculator
        self.gf = generator_calculator.gf
        
    def encode_block(self, data: List[int], ec_words: int) -> List[int]:
        """
        Encode a single block of data using Reed-Solomon encoding
        
        Args:
            data: List of data words to encode
            ec_words: Number of error correction words to generate
        
        Returns:
            List of error correction words
        """
        generator = self.generator_calc.generate_generator_polynomial(ec_words)
        
        # Create the message polynomial
        message = list(data) + [0] * ec_words
        
        # Perform polynomial division
        for i in range(len(data)):
            if message[i] == 0:
                continue
                
            factor = self.gf.log[message[i]]
            
            for j in range(len(generator)):
                message[i + j] ^= self.gf.exp[(self.gf.log[generator[j]] + factor) % 255]
        
        return message[-ec_words:]

class QRErrorCorrection:
    """
    Handles QR code error correction level configurations and block splitting
    """

    @staticmethod
    def get_raw_block_config(version: int, ec_level: str) -> List[int]:
        """Get raw block configuration for given version and EC level"""
        if version < 1 or version > 40 and ec_level not in EC_INDEX.keys():
            raise ValueError(f"Invalid version or EC level: {version}, {ec_level}")
        # Get block config from the table
        config = RS_BLOCK_TABLE[(version - 1) * 4 + EC_INDEX[ec_level]]
        return [config[i:i + 3] for i in range(0, len(config), 3)]
    
    @staticmethod
    def get_block_config(version: int, ec_level: str) -> List[RSBlock]:
        """Get RS block configuration for given version and EC level"""
        if version < 1 or version > 40 and ec_level not in EC_INDEX.keys():
            raise ValueError(f"Invalid version or EC level: {version}, {ec_level}")
        # Get block config from the table
        config = RS_BLOCK_TABLE[(version - 1) * 4 + EC_INDEX[ec_level]]
        # Split by 3 to get each block configuration section separately
        block_config = [config[i:i + 3] for i in range(0, len(config), 3)]
        
        return [
            RSBlock(total_words=total, data_words=data)
            for count, total, data in block_config
            for _ in range(count)
        ]
        
    def __init__(self, version: int, ec_level: str):
        self.version = version
        self.ec_level = ec_level.upper()
        
        self.blocks = self.get_block_config(version, self.ec_level)
        self.encoder = ReedSolomonEncoder(GeneratorPolynomialCalculator())
    
    def encode_data(self, data: List[int]) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Encode data using Reed-Solomon error correction
        
        Args:
            data: List of data words to encode
        
        Returns:
            Tuple of (data blocks, error correction blocks)
        """
        data_blocks = []
        ec_blocks = []
        
        data_idx = 0
        for block in self.blocks:
            # Split data into blocks
            block_data = data[data_idx:data_idx + block.data_words]
            data_idx += block.data_words
            data_blocks.append(block_data)
            
            # Generate error correction words for each block
            ec_words = self.encoder.encode_block(block_data, block.ec_words)
            ec_blocks.append(ec_words)
        
        return data_blocks, ec_blocks
