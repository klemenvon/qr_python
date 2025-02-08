from qrgen.utils import alignment_patterns
from qrgen.reedsolomon import get_rs_block_table

def get_total_modules(version):
    """Calculate total number of modules in a QR code of given version."""
    # Each version increases size by 4 modules
    return 21 + (version - 1) * 4

def get_usable_modules(version):
    """Calculate number of modules available for data and error correction."""
    size = get_total_modules(version)
    total_modules = size * size
    
    # Subtract finder patterns (3 x 7x7)
    finder_modules = 3 * 8 * 8
    
    # Subtract timing patterns
    timing_modules = (size - 16) * 2  # Horizontal and vertical
    
    # Subtract format information
    format_modules = 2 * 15

    # Version info modules
    if version >= 7:
        format_modules += 36
    
    # Subtract alignment patterns
    num_alignment = len(alignment_patterns[version-1])
    alignment_modules = 0
    if num_alignment > 0:
        alignment_modules = (num_alignment - 1) * 25
    
    unusable_modules = (finder_modules + timing_modules + format_modules + alignment_modules + 1)
    
    return total_modules - unusable_modules

def get_total_data_bits(version):
    """Convert usable modules to data bits (8 bits per byte)."""
    return get_usable_modules(version)

def get_allocated_bits(version, ec_level):
    """Calculate number of bits allocated for data and error correction."""
    config = get_rs_block_table(version, ec_level)
    block_config = [config[i:i + 3] for i in range(0, len(config), 3)]
    return sum([
        total * count
        for count, total, _ in block_config
    ]) * 8


# Print results for versions 1-5
for v in range(1, 40):
    print(f"Version {v}:")
    print(f"  Total modules: {get_total_modules(v)}x{get_total_modules(v)}")
    print(f"  Usable modules: {get_usable_modules(v)}")
    for ec in 'LMQH':
        print(f"  [{ec}]:")
        print(f"    Data bits capacity: {get_total_data_bits(v)}")
        print(f"    Allocated bits: {get_allocated_bits(v, ec)}")
        print()