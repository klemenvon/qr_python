
alignment_patterns = [
    [],         # Version 1 - No alignment patterns
    [6, 18],    # Version 2
    [6, 22],    # Version 3
    [6, 26],    # Version 4
    [6, 30],    # Version 5
    [6, 34],    # Version 6
    [6, 22, 38],# Version 7
    [6, 24, 42],# Version 8
    [6, 26, 46],# Version 9
    [6, 28, 50],# Version 10
    [6, 30, 54],# Version 11
    [6, 32, 58],# Version 12
    [6, 34, 62],# Version 13
    [6, 26, 46, 66],# Version 14
    [6, 26, 48, 70],# Version 15
    [6, 26, 50, 74],# Version 16
    [6, 30, 54, 78],# Version 17
    [6, 30, 56, 82],# Version 18
    [6, 30, 58, 86],# Version 19
    [6, 34, 62, 90],# Version 20
    [6, 28, 50, 72, 94],# Version 21
    [6, 26, 50, 74, 98],# Version 22
    [6, 30, 54, 78, 102],# Version 23
    [6, 28, 54, 80, 106],# Version 24
    [6, 32, 58, 84, 110],# Version 25
    [6, 30, 58, 86, 114],# Version 26
    [6, 34, 62, 90, 118],# Version 27
    [6, 26, 50, 74, 98, 122],# Version 28
    [6, 30, 54, 78, 102, 126],# Version 29
    [6, 26, 52, 78, 104, 130],# Version 30
    [6, 30, 56, 82, 108, 134],# Version 31
    [6, 34, 60, 86, 112, 138],# Version 32
    [6, 30, 58, 86, 114, 142],# Version 33
    [6, 34, 62, 90, 118, 146],# Version 34
    [6, 30, 54, 78, 102, 126, 150],# Version 35
    [6, 24, 50, 76, 102, 128, 154],# Version 36
    [6, 28, 54, 80, 106, 132, 158],# Version 37
    [6, 32, 58, 84, 110, 136, 162],# Version 38
    [6, 26, 54, 82, 110, 138, 166],# Version 39
    [6, 30, 58, 86, 114, 142, 170] # Version 40
]

def get_alignment_pattern_positions(version):
    if version == 1:
        return []
    locations = alignment_patterns[version-1]
    return [(x, y) for x in locations for y in locations]

def interleave_blocks(blocks, block_structure):
    """
    Interleave blocks according to the RS block structure
    blocks: The actual data or EC blocks to interleave
    block_structure: List of (count, total_words, data_words) tuples from RS config
    """
    interleaved = []
    current_block = 0
    
    # For each block group in the structure
    for count, total, data in block_structure:
        group_blocks = blocks[current_block:current_block + count]
        # Interleave this group
        for i in range(max(len(b) for b in group_blocks)):
            for block in group_blocks:
                if i < len(block):
                    interleaved.append(block[i])
        current_block += count
    
    return interleaved

def interleave_blocks_v2(data_blocks):
    # This one was breaking because we didn't interleave the blocks of same size together, instead just all of them...
    interleaved = []
    max_length = max(len(block) for block in data_blocks)
    for i in range(max_length):
        for block in data_blocks:
            if i < len(block):
                interleaved.append(block[i])
    return interleaved

def interleave_blocks_broken(data_blocks):
    # Lol, this is broken because if the blocks are of different lengths, it will simply disappear some data into the void
    interleaved = []
    for group in zip(*data_blocks):
        interleaved.extend(list(group))
    return interleaved
