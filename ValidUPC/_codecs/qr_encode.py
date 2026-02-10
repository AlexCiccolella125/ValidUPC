"""QR code encoder: byte mode, EC level L, versions 1-6."""

from PIL import Image, ImageDraw
from ValidUPC._codecs._gf256 import rs_encode
from ValidUPC._codecs._qr_tables import (
    VERSION_INFO, ALIGNMENT_POSITIONS, MASK_FUNCTIONS, FORMAT_INFO,
)

MODULE_SIZE = 10
QUIET_ZONE = 4


def save_qr(data: str, output_path: str) -> str:
    """Encode data as QR code and save as PNG."""
    img = generate_qr(data)
    full_path = output_path + ".png"
    img.save(full_path)
    return full_path


def generate_qr(data: str) -> Image.Image:
    """Encode data as a QR code and return a Pillow Image."""
    data_bytes = data.encode("utf-8")
    version = _select_version(len(data_bytes))
    size, total_cw, data_cw, ec_per_block, num_blocks = VERSION_INFO[version]

    # Encode data bits
    codewords = _encode_data(data_bytes, data_cw)

    # Error correction
    ec_codewords = _compute_ec(codewords, ec_per_block, num_blocks)

    # Interleave if multiple blocks
    final_data = _interleave(codewords, ec_codewords, num_blocks, ec_per_block)

    # Convert to bit stream
    bits = ""
    for cw in final_data:
        bits += format(cw, "08b")
    # Add remainder bits (versions 2-6 need 7 remainder bits)
    if version >= 2:
        bits += "0" * 7

    # Build matrix
    matrix = [[None] * size for _ in range(size)]
    reserved = [[False] * size for _ in range(size)]

    _place_finder_patterns(matrix, reserved, size)
    _place_timing_patterns(matrix, reserved, size)
    _place_alignment_patterns(matrix, reserved, version, size)
    _place_dark_module(matrix, reserved, version)
    _reserve_format_areas(matrix, reserved, size)

    _place_data_bits(matrix, reserved, bits, size)

    # Try all masks, pick best
    best_mask = 0
    best_penalty = float("inf")
    for mask_id in range(8):
        candidate = _apply_mask(matrix, reserved, mask_id, size)
        _write_format_info(candidate, mask_id, size)
        penalty = _compute_penalty(candidate, size)
        if penalty < best_penalty:
            best_penalty = penalty
            best_mask = mask_id

    # Apply best mask
    final = _apply_mask(matrix, reserved, best_mask, size)
    _write_format_info(final, best_mask, size)

    return _render(final, size)


def _select_version(data_len: int) -> int:
    """Select smallest QR version that fits the data in byte mode."""
    for v in range(1, 7):
        _, _, data_cw, _, _ = VERSION_INFO[v]
        # Byte mode overhead: 4 bits mode + 8 bits count = 12 bits = 1.5 bytes
        # Available data bytes = data_cw - 2 (for mode indicator and count)
        capacity = data_cw - 2  # conservative: 2 bytes overhead
        if data_len <= capacity:
            return v
    raise ValueError(f"Data too long ({data_len} bytes) for supported QR versions 1-6")


def _encode_data(data_bytes: bytes, data_cw: int) -> list[int]:
    """Encode data in byte mode and pad to fill data codewords."""
    bits = "0100"  # byte mode indicator
    bits += format(len(data_bytes), "08b")  # character count (8 bits for v1-9)
    for b in data_bytes:
        bits += format(b, "08b")

    # Add terminator (up to 4 zero bits)
    remaining = data_cw * 8 - len(bits)
    bits += "0" * min(4, remaining)

    # Pad to byte boundary
    while len(bits) % 8 != 0:
        bits += "0"

    # Convert to codewords
    codewords = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]

    # Pad with alternating 0xEC and 0x11
    pad_bytes = [0xEC, 0x11]
    i = 0
    while len(codewords) < data_cw:
        codewords.append(pad_bytes[i % 2])
        i += 1

    return codewords


def _compute_ec(data_cw: list[int], ec_per_block: int, num_blocks: int) -> list[list[int]]:
    """Compute RS error correction for each block."""
    block_size = len(data_cw) // num_blocks
    ec_blocks = []
    for i in range(num_blocks):
        block = data_cw[i * block_size:(i + 1) * block_size]
        ec = rs_encode(block, ec_per_block)
        ec_blocks.append(ec)
    return ec_blocks


def _interleave(data_cw: list[int], ec_blocks: list[list[int]],
                num_blocks: int, ec_per_block: int) -> list[int]:
    """Interleave data and EC codewords across blocks."""
    if num_blocks == 1:
        return data_cw + ec_blocks[0]

    block_size = len(data_cw) // num_blocks
    data_blocks = [data_cw[i * block_size:(i + 1) * block_size] for i in range(num_blocks)]

    result = []
    # Interleave data
    for i in range(block_size):
        for block in data_blocks:
            if i < len(block):
                result.append(block[i])
    # Interleave EC
    for i in range(ec_per_block):
        for block in ec_blocks:
            if i < len(block):
                result.append(block[i])
    return result


def _place_finder_patterns(matrix, reserved, size):
    """Place the three 7x7 finder patterns."""
    positions = [(0, 0), (0, size - 7), (size - 7, 0)]
    for r, c in positions:
        for dr in range(7):
            for dc in range(7):
                # Outer ring, inner ring, center
                if (dr in (0, 6) or dc in (0, 6) or
                        (2 <= dr <= 4 and 2 <= dc <= 4)):
                    matrix[r + dr][c + dc] = 1
                else:
                    matrix[r + dr][c + dc] = 0
                reserved[r + dr][c + dc] = True

        # White separators
        for i in range(8):
            for rr, cc in [(r - 1, c + i - 1), (r + 7, c + i - 1),
                           (r + i - 1, c - 1), (r + i - 1, c + 7)]:
                if 0 <= rr < size and 0 <= cc < size:
                    if matrix[rr][cc] is None:
                        matrix[rr][cc] = 0
                    reserved[rr][cc] = True
        # Extra corners of separator
        for rr, cc in [(r - 1, c - 1), (r - 1, c + 7), (r + 7, c - 1), (r + 7, c + 7)]:
            if 0 <= rr < size and 0 <= cc < size:
                if matrix[rr][cc] is None:
                    matrix[rr][cc] = 0
                reserved[rr][cc] = True


def _place_timing_patterns(matrix, reserved, size):
    """Place timing patterns in row 6 and column 6."""
    for i in range(8, size - 8):
        val = 1 if i % 2 == 0 else 0
        if matrix[6][i] is None:
            matrix[6][i] = val
            reserved[6][i] = True
        if matrix[i][6] is None:
            matrix[i][6] = val
            reserved[i][6] = True


def _place_alignment_patterns(matrix, reserved, version, size):
    """Place alignment patterns for version 2+."""
    positions = ALIGNMENT_POSITIONS[version]
    if not positions:
        return

    centers = []
    for r in positions:
        for c in positions:
            # Skip if overlapping with finder patterns
            if (r, c) in [(6, 6), (6, size - 7), (size - 7, 6)]:
                continue
            # More careful overlap check
            overlap = False
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    if reserved[r + dr][c + dc]:
                        overlap = True
                        break
                if overlap:
                    break
            if not overlap:
                centers.append((r, c))

    for r, c in centers:
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if abs(dr) == 2 or abs(dc) == 2 or (dr == 0 and dc == 0):
                    matrix[r + dr][c + dc] = 1
                else:
                    matrix[r + dr][c + dc] = 0
                reserved[r + dr][c + dc] = True


def _place_dark_module(matrix, reserved, version):
    """Place the always-dark module."""
    r = 4 * version + 9
    matrix[r][8] = 1
    reserved[r][8] = True


def _reserve_format_areas(matrix, reserved, size):
    """Reserve cells for format information (initialized to 0, overwritten later)."""
    # Around top-left finder
    for i in range(9):
        if matrix[8][i] is None:
            matrix[8][i] = 0
        reserved[8][i] = True
        if matrix[i][8] is None:
            matrix[i][8] = 0
        reserved[i][8] = True
    # Around top-right finder
    for i in range(8):
        if matrix[8][size - 1 - i] is None:
            matrix[8][size - 1 - i] = 0
        reserved[8][size - 1 - i] = True
    # Around bottom-left finder
    for i in range(7):
        if matrix[size - 1 - i][8] is None:
            matrix[size - 1 - i][8] = 0
        reserved[size - 1 - i][8] = True


def _place_data_bits(matrix, reserved, bits, size):
    """Place data bits in the QR zigzag pattern."""
    bit_idx = 0
    # Columns go right-to-left in pairs, skipping column 6
    col = size - 1
    going_up = True

    while col >= 0:
        if col == 6:
            col -= 1
            continue

        rows = range(size - 1, -1, -1) if going_up else range(size)
        for row in rows:
            for dc in [0, -1]:
                c = col + dc
                if c < 0:
                    continue
                if not reserved[row][c] and matrix[row][c] is None:
                    if bit_idx < len(bits):
                        matrix[row][c] = int(bits[bit_idx])
                        bit_idx += 1
                    else:
                        matrix[row][c] = 0

        going_up = not going_up
        col -= 2


def _apply_mask(matrix, reserved, mask_id, size):
    """Apply a mask pattern to a copy of the matrix."""
    result = [row[:] for row in matrix]
    mask_fn = MASK_FUNCTIONS[mask_id]
    for r in range(size):
        for c in range(size):
            if not reserved[r][c] and result[r][c] is not None:
                if mask_fn(r, c):
                    result[r][c] ^= 1
    return result


def _write_format_info(matrix, mask_id, size):
    """Write format information bits into the matrix."""
    info = FORMAT_INFO[mask_id]
    bits = format(info, "015b")

    # Positions around top-left finder
    # Horizontal: columns 0-7 (skip col 6 -> use 8), row 8
    h_positions = [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
                   (8, 7), (8, 8), (8, size - 8), (8, size - 7),
                   (8, size - 6), (8, size - 5), (8, size - 4),
                   (8, size - 3), (8, size - 2)]
    # Vertical: rows 0-7 (skip row 6 -> use 8), column 8
    v_positions = [(0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8),
                   (7, 8), (8, 8), (size - 7, 8), (size - 6, 8),
                   (size - 5, 8), (size - 4, 8), (size - 3, 8),
                   (size - 2, 8), (size - 1, 8)]

    for i, (r, c) in enumerate(h_positions):
        matrix[r][c] = int(bits[i])
    for i, (r, c) in enumerate(v_positions):
        matrix[r][c] = int(bits[14 - i])


def _compute_penalty(matrix, size):
    """Compute penalty score for mask evaluation."""
    penalty = 0

    # Rule 1: runs of 5+ same-color modules
    for r in range(size):
        count = 1
        for c in range(1, size):
            if matrix[r][c] == matrix[r][c - 1]:
                count += 1
            else:
                if count >= 5:
                    penalty += 3 + (count - 5)
                count = 1
        if count >= 5:
            penalty += 3 + (count - 5)

    for c in range(size):
        count = 1
        for r in range(1, size):
            if matrix[r][c] == matrix[r - 1][c]:
                count += 1
            else:
                if count >= 5:
                    penalty += 3 + (count - 5)
                count = 1
        if count >= 5:
            penalty += 3 + (count - 5)

    # Rule 2: 2x2 blocks
    for r in range(size - 1):
        for c in range(size - 1):
            val = matrix[r][c]
            if val == matrix[r][c + 1] == matrix[r + 1][c] == matrix[r + 1][c + 1]:
                penalty += 3

    # Rule 3: finder-like patterns
    pattern_a = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    pattern_b = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]
    for r in range(size):
        for c in range(size - 10):
            row_seg = [matrix[r][c + i] for i in range(11)]
            if row_seg == pattern_a or row_seg == pattern_b:
                penalty += 40
    for c in range(size):
        for r in range(size - 10):
            col_seg = [matrix[r + i][c] for i in range(11)]
            if col_seg == pattern_a or col_seg == pattern_b:
                penalty += 40

    # Rule 4: proportion of dark modules
    total = size * size
    dark = sum(matrix[r][c] for r in range(size) for c in range(size))
    pct = (dark * 100) // total
    prev5 = abs(pct - pct % 5 - 50) // 5
    next5 = abs(pct - pct % 5 + 5 - 50) // 5
    penalty += min(prev5, next5) * 10

    return penalty


def _render(matrix, size) -> Image.Image:
    """Render the QR matrix to a Pillow Image."""
    img_size = (size + 2 * QUIET_ZONE) * MODULE_SIZE
    img = Image.new("1", (img_size, img_size), 1)
    draw = ImageDraw.Draw(img)
    for r in range(size):
        for c in range(size):
            if matrix[r][c] == 1:
                x = (QUIET_ZONE + c) * MODULE_SIZE
                y = (QUIET_ZONE + r) * MODULE_SIZE
                draw.rectangle(
                    [x, y, x + MODULE_SIZE - 1, y + MODULE_SIZE - 1],
                    fill=0,
                )
    return img
