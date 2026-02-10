from PIL import Image
from ValidUPC._codecs.barcode_encode import L_CODES, R_CODES, G_CODES, EAN13_PARITY

# Build lookup dicts: 7-char bit pattern -> (digit, code_type)
_L_LOOKUP = {p: i for i, p in enumerate(L_CODES)}
_R_LOOKUP = {p: i for i, p in enumerate(R_CODES)}
_G_LOOKUP = {p: i for i, p in enumerate(G_CODES)}


def decode_barcode_from_image(image_path: str) -> list[dict]:
    """Decode barcodes from an image file.

    Returns list of dicts with 'code_str' and 'barcode_type' keys.
    """
    img = Image.open(image_path)
    gray = img.convert("L")
    width, height = gray.size

    # Try multiple scanlines for robustness
    for y_pct in [0.5, 0.4, 0.6, 0.3, 0.7]:
        y = int(height * y_pct)
        row = [gray.getpixel((x, y)) for x in range(width)]
        binary = [0 if p < 128 else 1 for p in row]
        result = _try_decode_scanline(binary)
        if result:
            return [result]

    return []


def _try_decode_scanline(binary: list[int]) -> dict | None:
    """Try to decode a barcode from a binary scanline."""
    runs = _extract_runs(binary)

    # Skip leading white space
    start = 0
    if runs and runs[0][0] == 1:  # starts with white
        start = 1

    # Need at minimum: start(3 bars) + left(24 bars) + middle(5 bars) + right(24 bars) + end(3 bars) = 59 bars
    remaining = runs[start:]
    if len(remaining) < 59:
        return None

    # Find the unit width from the start guard (first 3 bars should be ~equal width)
    unit = (remaining[0][1] + remaining[1][1] + remaining[2][1]) / 3

    # Verify start guard: black-white-black, each ~1 unit
    if remaining[0][0] != 0 or remaining[1][0] != 1 or remaining[2][0] != 0:
        return None

    pos = 3  # past start guard

    # Decode left digits (each digit = 2 bars black + 2 bars white = 4 runs = 7 modules)
    left_digits = []
    left_codes = []  # track L or G for each digit
    for _ in range(6):
        if pos + 4 > len(remaining):
            return None
        modules = _runs_to_modules(remaining[pos:pos + 4], unit)
        if modules is None or len(modules) != 7:
            return None
        digit, code_type = _lookup_digit(modules)
        if digit is None:
            return None
        left_digits.append(digit)
        left_codes.append(code_type)
        pos += 4

    # Verify middle guard: white-black-white-black-white (5 runs, each ~1 unit)
    if pos + 5 > len(remaining):
        return None
    mid_modules = _runs_to_modules(remaining[pos:pos + 5], unit)
    if mid_modules != "01010":
        return None
    pos += 5

    # Decode right digits
    right_digits = []
    for _ in range(6):
        if pos + 4 > len(remaining):
            return None
        modules = _runs_to_modules(remaining[pos:pos + 4], unit)
        if modules is None or len(modules) != 7:
            return None
        digit, code_type = _lookup_digit(modules)
        if digit is None:
            return None
        right_digits.append(digit)
        pos += 4

    # Determine barcode type from left-side code types
    parity_str = "".join(left_codes)

    if parity_str == "LLLLLL":
        # UPC-A: all L-codes on left
        code_str = "".join(str(d) for d in left_digits + right_digits)
        return {"code_str": code_str, "barcode_type": "UPC_A"}
    elif parity_str in EAN13_PARITY:
        # EAN-13: mixed L/G on left, first digit derived from parity
        first_digit = EAN13_PARITY.index(parity_str)
        code_str = str(first_digit) + "".join(str(d) for d in left_digits + right_digits)
        return {"code_str": code_str, "barcode_type": "EAN_13"}

    return None


def decode_ean8_from_image(image_path: str) -> list[dict]:
    """Decode EAN-8 barcodes from an image file."""
    img = Image.open(image_path)
    gray = img.convert("L")
    width, height = gray.size

    for y_pct in [0.5, 0.4, 0.6, 0.3, 0.7]:
        y = int(height * y_pct)
        row = [gray.getpixel((x, y)) for x in range(width)]
        binary = [0 if p < 128 else 1 for p in row]
        result = _try_decode_ean8(binary)
        if result:
            return [result]

    return []


def _try_decode_ean8(binary: list[int]) -> dict | None:
    """Try to decode an EAN-8 from a binary scanline."""
    runs = _extract_runs(binary)

    start = 0
    if runs and runs[0][0] == 1:
        start = 1

    remaining = runs[start:]
    # EAN-8: start(3) + left(16 bars for 4 digits) + middle(5) + right(16) + end(3) = 43 bars
    if len(remaining) < 43:
        return None

    unit = (remaining[0][1] + remaining[1][1] + remaining[2][1]) / 3

    if remaining[0][0] != 0 or remaining[1][0] != 1 or remaining[2][0] != 0:
        return None

    pos = 3

    # 4 left digits (L-code)
    left_digits = []
    for _ in range(4):
        if pos + 4 > len(remaining):
            return None
        modules = _runs_to_modules(remaining[pos:pos + 4], unit)
        if modules is None or len(modules) != 7:
            return None
        digit, code_type = _lookup_digit(modules)
        if digit is None:
            return None
        left_digits.append(digit)
        pos += 4

    # Middle guard
    if pos + 5 > len(remaining):
        return None
    mid_modules = _runs_to_modules(remaining[pos:pos + 5], unit)
    if mid_modules != "01010":
        return None
    pos += 5

    # 4 right digits (R-code)
    right_digits = []
    for _ in range(4):
        if pos + 4 > len(remaining):
            return None
        modules = _runs_to_modules(remaining[pos:pos + 4], unit)
        if modules is None or len(modules) != 7:
            return None
        digit, code_type = _lookup_digit(modules)
        if digit is None:
            return None
        right_digits.append(digit)
        pos += 4

    code_str = "".join(str(d) for d in left_digits + right_digits)
    return {"code_str": code_str, "barcode_type": "EAN_8"}


def _extract_runs(binary: list[int]) -> list[tuple[int, int]]:
    """Extract consecutive runs of same value. Returns [(value, length), ...]."""
    if not binary:
        return []
    runs = []
    current = binary[0]
    length = 1
    for pixel in binary[1:]:
        if pixel == current:
            length += 1
        else:
            runs.append((current, length))
            current = pixel
            length = 1
    runs.append((current, length))
    return runs


def _runs_to_modules(runs: list[tuple[int, int]], unit: float) -> str | None:
    """Convert pixel-width runs to module-width bit string."""
    modules = ""
    for value, length in runs:
        n = max(1, round(length / unit))
        bit = "1" if value == 0 else "0"  # black pixels -> 1 in encoding tables
        modules += bit * n
    return modules


def _lookup_digit(modules: str) -> tuple[int | None, str]:
    """Look up a 7-module pattern in L, R, G code tables."""
    if modules in _L_LOOKUP:
        return _L_LOOKUP[modules], "L"
    if modules in _R_LOOKUP:
        return _R_LOOKUP[modules], "R"
    if modules in _G_LOOKUP:
        return _G_LOOKUP[modules], "G"
    return None, ""
