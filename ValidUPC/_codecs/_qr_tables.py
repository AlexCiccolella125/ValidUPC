"""QR code specification tables for versions 1-6, EC level L."""

# Version -> (size, total_codewords, data_codewords, ec_codewords_per_block, num_blocks)
VERSION_INFO = {
    1: (21, 26, 19, 7, 1),
    2: (25, 44, 34, 10, 1),
    3: (29, 70, 55, 15, 1),
    4: (33, 100, 80, 20, 1),
    5: (37, 134, 108, 26, 1),
    6: (41, 172, 136, 18, 2),
}

# Alignment pattern center coordinates per version
ALIGNMENT_POSITIONS = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
}

# 8 mask pattern functions: (row, col) -> bool (True = flip module)
MASK_FUNCTIONS = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]


def bch_format_info(data_5bits: int) -> int:
    """Compute BCH(15,5) for format information.

    Input: 5-bit data (EC level 2 bits + mask 3 bits)
    Returns: 15-bit format info XORed with mask pattern.
    """
    # Generator polynomial for BCH(15,5): x^10 + x^8 + x^5 + x^4 + x^2 + x + 1
    g = 0b10100110111
    d = data_5bits << 10
    for i in range(4, -1, -1):
        if d & (1 << (i + 10)):
            d ^= g << i
    result = (data_5bits << 10) | d
    # XOR with mask pattern
    result ^= 0b101010000010010
    return result


# Precompute format info for EC level L (01) with each mask (0-7)
FORMAT_INFO = {}
for mask in range(8):
    data = (0b01 << 3) | mask  # EC level L = 01
    FORMAT_INFO[mask] = bch_format_info(data)
