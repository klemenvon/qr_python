from qrgen.utils import interleave_blocks

block1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
block2 = [10, 11, 12, 13, 14, 15, 16, 17]
print(len(block1))
print(len(block2))
blocks = [block1, block2]
interleaved = interleave_blocks(blocks)
print(interleaved)