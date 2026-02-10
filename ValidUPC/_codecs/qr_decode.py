"""QR code decoder for clean programmatic images."""

from PIL import Image
from ValidUPC._codecs._qr_tables import MASK_FUNCTIONS, VERSION_INFO


def decode_qr_from_image(image_path: str) -> list[str]:
    """Decode QR codes from an image. Returns list of decoded strings."""
    img = Image.open(image_path)
    gray = img.convert("L")
    width, height = gray.size

    # Binarize
    binary = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(0 if gray.getpixel((x, y)) < 128 else 1)
        binary.append(row)

    # Find finder patterns
    finders = _find_finder_patterns(binary, width, height)
    if len(finders) < 3:
        return []

    # Determine module size and grid
    grid_info = _determine_grid(finders, width, height)
    if grid_info is None:
        return []

    size = grid_info["size"]
    module_size = grid_info["module_size"]
    origin_x = grid_info["origin_x"]
    origin_y = grid_info["origin_y"]

    # Sample the grid
    matrix = _sample_grid(binary, size, module_size, origin_x, origin_y)

    # Read format info
    ec_level, mask_id = _read_format_info(matrix, size)
    if mask_id is None:
        return []

    # Determine version from size
    version = (size - 17) // 4

    # Build reserved mask
    reserved = [[False] * size for _ in range(size)]
    _mark_reserved(reserved, version, size)

    # Unmask
    mask_fn = MASK_FUNCTIONS[mask_id]
    for r in range(size):
        for c in range(size):
            if not reserved[r][c]:
                if mask_fn(r, c):
                    matrix[r][c] ^= 1

    # Extract data bits
    bits = _extract_data_bits(matrix, reserved, size)

    # Decode byte mode
    data = _decode_data(bits, version)
    if data is not None:
        return [data]

    return []


def _find_finder_patterns(binary, width, height):
    """Find finder pattern centers by scanning for 1:1:3:1:1 ratio."""
    candidates = []

    # Scan rows
    for y in range(height):
        runs = []
        current = binary[y][0]
        length = 1
        start = 0
        for x in range(1, width):
            if binary[y][x] == current:
                length += 1
            else:
                runs.append((current, length, start))
                start = x
                current = binary[y][x]
                length = 1
        runs.append((current, length, start))

        # Look for black-white-black-white-black with 1:1:3:1:1 ratio
        for i in range(len(runs) - 4):
            if runs[i][0] != 0:  # must start with black
                continue
            widths = [runs[i + j][1] for j in range(5)]
            total = sum(widths)
            unit = total / 7.0
            if unit < 1:
                continue
            ratios = [w / unit for w in widths]
            expected = [1, 1, 3, 1, 1]
            if all(abs(r - e) < 0.75 for r, e in zip(ratios, expected)):
                cx = runs[i][2] + total // 2
                cy = y
                # Verify vertically
                if _verify_vertical(binary, cx, cy, width, height, unit):
                    candidates.append((cx, cy, unit))

    # Cluster nearby candidates
    return _cluster_centers(candidates)


def _verify_vertical(binary, cx, cy, width, height, unit):
    """Verify a finder pattern center vertically."""
    if cx < 0 or cx >= width:
        return False

    # Scan up and down from center
    expected_half = int(unit * 3.5) + 2
    y_start = max(0, cy - expected_half)
    y_end = min(height, cy + expected_half + 1)

    runs = []
    current = binary[y_start][cx]
    length = 1
    for y in range(y_start + 1, y_end):
        if binary[y][cx] == current:
            length += 1
        else:
            runs.append((current, length))
            current = binary[y][cx]
            length = 1
    runs.append((current, length))

    # Find the central black run
    black_runs = [(i, r) for i, r in enumerate(runs) if r[0] == 0 and r[1] > unit * 2]
    if not black_runs:
        return False

    for idx, (_, bl) in black_runs:
        if idx >= 2 and idx + 2 < len(runs):
            widths = [runs[idx - 2 + j][1] for j in range(5)]
            total = sum(widths)
            v_unit = total / 7.0
            ratios = [w / v_unit for w in widths]
            expected = [1, 1, 3, 1, 1]
            if all(abs(r - e) < 1.0 for r, e in zip(ratios, expected)):
                return True

    return False


def _cluster_centers(candidates):
    """Cluster nearby finder pattern candidates."""
    if not candidates:
        return []

    clusters = []
    used = [False] * len(candidates)

    for i, (cx, cy, unit) in enumerate(candidates):
        if used[i]:
            continue
        cluster_x = [cx]
        cluster_y = [cy]
        cluster_unit = [unit]
        used[i] = True

        for j, (cx2, cy2, unit2) in enumerate(candidates):
            if used[j]:
                continue
            dist = ((cx - cx2) ** 2 + (cy - cy2) ** 2) ** 0.5
            if dist < unit * 5:
                cluster_x.append(cx2)
                cluster_y.append(cy2)
                cluster_unit.append(unit2)
                used[j] = True

        avg_x = sum(cluster_x) // len(cluster_x)
        avg_y = sum(cluster_y) // len(cluster_y)
        avg_unit = sum(cluster_unit) / len(cluster_unit)
        clusters.append((avg_x, avg_y, avg_unit))

    return clusters


def _determine_grid(finders, width, height):
    """Determine QR grid parameters from finder patterns."""
    if len(finders) < 3:
        return None

    # Sort by position to identify top-left, top-right, bottom-left
    # Top-left is the one closest to origin (0,0)
    finders = sorted(finders, key=lambda f: f[0] ** 2 + f[1] ** 2)

    # The finder closest to (0,0) is top-left
    tl = finders[0]

    # Of the remaining two, the one with similar y to tl is top-right,
    # the one with similar x to tl is bottom-left
    remaining = finders[1:3]
    if abs(remaining[0][1] - tl[1]) < abs(remaining[1][1] - tl[1]):
        tr = remaining[0]
        bl = remaining[1]
    else:
        tr = remaining[1]
        bl = remaining[0]

    # Make sure tr is to the right and bl is below
    if tr[0] < tl[0]:
        tr, bl = bl, tr

    # Module size from finder pattern unit (finder is 7 modules)
    module_size = tl[2]

    # Distance from tl to tr center should be (size - 7) modules
    dist_h = ((tr[0] - tl[0]) ** 2 + (tr[1] - tl[1]) ** 2) ** 0.5
    size_estimate = round(dist_h / module_size) + 7

    # Round to valid QR size (21, 25, 29, 33, 37, 41)
    valid_sizes = [21, 25, 29, 33, 37, 41]
    size = min(valid_sizes, key=lambda s: abs(s - size_estimate))

    # Origin is top-left of the QR code (center of TL finder minus 3.5 modules)
    origin_x = tl[0] - 3.5 * module_size
    origin_y = tl[1] - 3.5 * module_size

    return {
        "size": size,
        "module_size": module_size,
        "origin_x": origin_x,
        "origin_y": origin_y,
    }


def _sample_grid(binary, size, module_size, origin_x, origin_y):
    """Sample the module grid from the binary image."""
    height = len(binary)
    width = len(binary[0]) if binary else 0
    matrix = [[0] * size for _ in range(size)]

    for r in range(size):
        for c in range(size):
            # Sample at center of each module
            x = int(origin_x + (c + 0.5) * module_size)
            y = int(origin_y + (r + 0.5) * module_size)
            if 0 <= x < width and 0 <= y < height:
                matrix[r][c] = 1 if binary[y][x] == 0 else 0  # black=1
            else:
                matrix[r][c] = 0

    return matrix


def _read_format_info(matrix, size):
    """Read format information from the matrix."""
    # Read from around top-left finder (horizontal)
    h_positions = [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
                   (8, 7), (8, 8), (8, size - 8), (8, size - 7),
                   (8, size - 6), (8, size - 5), (8, size - 4),
                   (8, size - 3), (8, size - 2)]

    bits_h = 0
    for i, (r, c) in enumerate(h_positions):
        if matrix[r][c]:
            bits_h |= (1 << (14 - i))

    # Unmask with format mask
    info = bits_h ^ 0b101010000010010

    # Extract EC level (bits 13-14) and mask (bits 10-12)
    ec_level = (info >> 13) & 0b11
    mask_id = (info >> 10) & 0b111

    # Validate: for our images, EC level should be L (01)
    if 0 <= mask_id <= 7:
        return ec_level, mask_id

    return None, None


def _mark_reserved(reserved, version, size):
    """Mark all reserved (non-data) cells."""
    # Finder patterns + separators
    for r in range(9):
        for c in range(9):
            reserved[r][c] = True
    for r in range(9):
        for c in range(size - 8, size):
            reserved[r][c] = True
    for r in range(size - 8, size):
        for c in range(9):
            reserved[r][c] = True

    # Timing patterns
    for i in range(size):
        reserved[6][i] = True
        reserved[i][6] = True

    # Alignment patterns (version 2+)
    from ValidUPC._codecs._qr_tables import ALIGNMENT_POSITIONS
    positions = ALIGNMENT_POSITIONS.get(version, [])
    if positions:
        for r in positions:
            for c in positions:
                overlap = False
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < size and 0 <= cc < size:
                            # Check if in finder area
                            if ((rr < 9 and cc < 9) or
                                    (rr < 9 and cc >= size - 8) or
                                    (rr >= size - 8 and cc < 9)):
                                overlap = True
                                break
                    if overlap:
                        break
                if not overlap:
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            rr, cc = r + dr, c + dc
                            if 0 <= rr < size and 0 <= cc < size:
                                reserved[rr][cc] = True

    # Dark module
    reserved[4 * version + 9][8] = True

    # Format info areas
    for i in range(9):
        reserved[8][i] = True
        reserved[i][8] = True
    for i in range(8):
        reserved[8][size - 1 - i] = True
    for i in range(7):
        reserved[size - 1 - i][8] = True


def _extract_data_bits(matrix, reserved, size):
    """Extract data bits in the QR zigzag pattern."""
    bits = []
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
                if not reserved[row][c]:
                    bits.append(matrix[row][c])

        going_up = not going_up
        col -= 2

    return bits


def _decode_data(bits, version):
    """Decode byte-mode data from extracted bits."""
    if len(bits) < 12:
        return None

    # Read mode indicator (4 bits)
    mode = 0
    for i in range(4):
        mode = (mode << 1) | bits[i]

    if mode != 0b0100:  # byte mode
        return None

    # Character count (8 bits for versions 1-9)
    count = 0
    for i in range(4, 12):
        count = (count << 1) | bits[i]

    if len(bits) < 12 + count * 8:
        return None

    # Extract bytes
    data = []
    for i in range(count):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[12 + i * 8 + j]
        data.append(byte)

    return bytes(data).decode("utf-8")
