## File defining the mask ptterns to be applied to the QR Code.

def apply_mask(modules, data_mask, pattern_number):
    """
    Applies a mask pattern to the modules
    """
    mask = mask_patterns[pattern_number]
    for i, row in enumerate(modules):
        for j, _ in enumerate(row):
            if data_mask[i][j]:
                modules[i][j] = not modules[i][j] if mask(i, j) else modules[i][j]

def mask_0(i, j):
    return (i + j) % 2 == 0

def mask_1(i, j):
    return i % 2 == 0

def mask_2(i, j):
    return j % 3 == 0

def mask_3(i, j):
    return (i + j) % 3 == 0

def mask_4(i, j):
    return (i // 2 + j // 3) % 2 == 0

def mask_5(i, j):
    return (i * j) % 2 + (i * j) % 3 == 0

def mask_6(i, j):
    return ((i * j) % 2 + (i * j) % 3) % 2 == 0

def mask_7(i, j):
    return ((i + j) % 2 + (i * j) % 3) % 2 == 0

mask_patterns = [mask_0, mask_1, mask_2, mask_3, mask_4, mask_5, mask_6, mask_7]

def condition_1(modules):
    """Checks for repeated patterns of 5 or more horizontally"""
    total_penalty = 0
    for row in modules:
        current_color = row[0]
        count = 1
        for j, color in enumerate(row):
            if j == 0:
                continue
            if color == current_color:
                count += 1
            else:
                if count >= 5:
                    total_penalty += count - 2
                current_color = color
                count = 1
    return total_penalty

def condition_2(modules):
    """Checks for blocks of 2x2 black or white modules"""
    total_penalty = 0
    for i in range(len(modules) - 1):
        for j in range(len(modules) - 1):
            if modules[i][j] == modules[i][j + 1] == modules[i + 1][j] == modules[i + 1][j + 1]:
                total_penalty += 3
    return total_penalty

def condition_3(modules):
    """Checks for patterns of 1:1:3:1:1:4"""
    pattern = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    total_penalty = 0
    # Check rows
    for row in modules:
        for i in range(len(row) - 10):
            if row[i:i+11] == pattern:
                total_penalty += 40
    # Check columns
    for j in range(len(modules)):
        column = [row[j] for row in modules]
        for i in range(len(column) - 10):
            if column[i:i+11] == pattern:
                total_penalty += 40
    return total_penalty

def condition_4(modules):
    """Check for the ratio of dark to light modules"""
    total_penalty = 0
    dark_count = sum([sum([1 for module in row if module]) for row in modules])
    ratio = dark_count / (len(modules) ** 2)
    ratio = abs(ratio - 0.5) * 100
    ratio = int(ratio)
    total_penalty += ratio // 5 * 10
    return total_penalty

def evaluate_mask(modules):
    """Evaluates the penalty score for the mask pattern"""
    penalty = 0
    penalty += condition_1(modules)
    penalty += condition_2(modules)
    penalty += condition_3(modules)
    penalty += condition_4(modules)
    return penalty
