from PIL import Image, ImageDraw

# L-code patterns (left side of UPC-A/EAN-8, and EAN-13 L-parity digits)
L_CODES = [
    "0001101", "0011001", "0010011", "0111101", "0100011",
    "0110001", "0101111", "0111011", "0110111", "0001011",
]

# R-code = bitwise complement of L-code (right side digits)
R_CODES = [p.translate(str.maketrans("01", "10")) for p in L_CODES]

# G-code = reverse of R-code (for EAN-13 mixed parity)
G_CODES = [p[::-1] for p in R_CODES]

# EAN-13 first-digit parity table (L or G for each of the 6 left-side digits)
EAN13_PARITY = [
    "LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
    "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL",
]

START_GUARD = "101"
MIDDLE_GUARD = "01010"
END_GUARD = "101"

MODULE_WIDTH = 3
BAR_HEIGHT = 100
QUIET_ZONE = 9


def encode_upc_a(digits: str) -> str:
    """Encode a 12-digit UPC-A code to a bit pattern string."""
    bits = START_GUARD
    for d in digits[:6]:
        bits += L_CODES[int(d)]
    bits += MIDDLE_GUARD
    for d in digits[6:]:
        bits += R_CODES[int(d)]
    bits += END_GUARD
    return bits


def encode_ean_13(digits: str) -> str:
    """Encode a 13-digit EAN-13 code to a bit pattern string."""
    parity = EAN13_PARITY[int(digits[0])]
    bits = START_GUARD
    for i, d in enumerate(digits[1:7]):
        if parity[i] == "L":
            bits += L_CODES[int(d)]
        else:
            bits += G_CODES[int(d)]
    bits += MIDDLE_GUARD
    for d in digits[7:]:
        bits += R_CODES[int(d)]
    bits += END_GUARD
    return bits


def encode_ean_8(digits: str) -> str:
    """Encode an 8-digit EAN-8 code to a bit pattern string."""
    bits = START_GUARD
    for d in digits[:4]:
        bits += L_CODES[int(d)]
    bits += MIDDLE_GUARD
    for d in digits[4:]:
        bits += R_CODES[int(d)]
    bits += END_GUARD
    return bits


def render_barcode(bit_pattern: str, output_path: str,
                   image_format: str = "png") -> str:
    """Render a bit pattern to a barcode image file."""
    if image_format == "svg":
        return _render_svg(bit_pattern, output_path)
    return _render_png(bit_pattern, output_path)


def _render_png(bit_pattern: str, output_path: str) -> str:
    total_modules = len(bit_pattern) + 2 * QUIET_ZONE
    width = total_modules * MODULE_WIDTH
    height = BAR_HEIGHT
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)
    for i, bit in enumerate(bit_pattern):
        if bit == "1":
            x = (QUIET_ZONE + i) * MODULE_WIDTH
            draw.rectangle([x, 0, x + MODULE_WIDTH - 1, height - 1], fill=0)
    full_path = output_path + ".png"
    img.save(full_path)
    return full_path


def _render_svg(bit_pattern: str, output_path: str) -> str:
    total_modules = len(bit_pattern) + 2 * QUIET_ZONE
    width = total_modules * MODULE_WIDTH
    height = BAR_HEIGHT
    rects = []
    for i, bit in enumerate(bit_pattern):
        if bit == "1":
            x = (QUIET_ZONE + i) * MODULE_WIDTH
            rects.append(f'<rect x="{x}" y="0" width="{MODULE_WIDTH}" height="{height}"/>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<rect width="{width}" height="{height}" fill="white"/>'
        + "".join(rects)
        + "</svg>"
    )
    full_path = output_path + ".svg"
    with open(full_path, "w") as f:
        f.write(svg)
    return full_path
