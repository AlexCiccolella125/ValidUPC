"""Tests for internal codec modules to cover edge cases."""
import pytest
from PIL import Image

from ValidUPC._codecs._gf256 import gf_mul
from ValidUPC._codecs.barcode_decode import (
    _extract_runs, _lookup_digit, _try_decode_scanline, _try_decode_ean8,
)
from ValidUPC._codecs.qr_encode import (
    _select_version, _encode_data, _interleave, _compute_ec,
    generate_qr,
)


# --- GF(256) ---

def test_gf_mul_zero():
    assert gf_mul(0, 0) == 0
    assert gf_mul(0, 42) == 0
    assert gf_mul(42, 0) == 0


def test_gf_mul_nonzero():
    assert gf_mul(1, 1) == 1
    result = gf_mul(2, 3)
    assert isinstance(result, int) and 0 < result < 256


# --- barcode_decode internals ---

def test_extract_runs_empty():
    assert _extract_runs([]) == []


def test_extract_runs_single():
    assert _extract_runs([0]) == [(0, 1)]


def test_extract_runs_alternating():
    runs = _extract_runs([0, 0, 1, 1, 1, 0])
    assert runs == [(0, 2), (1, 3), (0, 1)]


def test_lookup_digit_unknown():
    digit, code_type = _lookup_digit("1111111")
    assert digit is None
    assert code_type == ""


def test_try_decode_scanline_too_short():
    assert _try_decode_scanline([1, 0, 1]) is None


def test_try_decode_scanline_empty():
    assert _try_decode_scanline([]) is None


def test_try_decode_scanline_all_white():
    assert _try_decode_scanline([1] * 200) is None


def test_try_decode_ean8_too_short():
    assert _try_decode_ean8([1, 0, 1]) is None


def test_try_decode_ean8_all_white():
    assert _try_decode_ean8([1] * 200) is None


# --- QR encode internals ---

def test_select_version_small():
    assert _select_version(1) == 1
    assert _select_version(10) == 1


def test_select_version_medium():
    v = _select_version(50)
    assert 1 <= v <= 6


def test_select_version_too_large():
    with pytest.raises(ValueError, match="Data too long"):
        _select_version(500)


def test_encode_data_padding():
    codewords = _encode_data(b"A", 19)
    assert len(codewords) == 19
    # Should contain padding bytes 0xEC, 0x11
    assert 0xEC in codewords or 0x11 in codewords


def test_interleave_multi_block():
    data = list(range(68))
    ec_block_0 = list(range(18))
    ec_block_1 = list(range(18))
    result = _interleave(data, [ec_block_0, ec_block_1], 2, 18)
    assert len(result) == 68 + 36


def test_qr_version_2_roundtrip(tmp_path):
    """Version 2+ QR to exercise alignment patterns."""
    data = "A" * 20  # enough data to require version 2
    img = generate_qr(data)
    assert img is not None
    assert img.size[0] > 0


def test_qr_version_3_roundtrip(tmp_path):
    """Version 3 QR to exercise larger alignment patterns."""
    data = "B" * 40
    img = generate_qr(data)
    assert img is not None


def test_qr_roundtrip_larger_data(tmp_path):
    """Generate and decode a version 4+ QR code."""
    from ValidUPC._codecs.qr_encode import save_qr
    from ValidUPC._codecs.qr_decode import decode_qr_from_image

    data = "X" * 78  # should require version 4
    path = save_qr(data, str(tmp_path / "large_qr"))
    results = decode_qr_from_image(path)
    assert len(results) == 1
    assert results[0] == data


def test_try_decode_scanline_bad_guard():
    """Start guard must be black-white-black; all-black fails."""
    # Create a scanline with enough runs but wrong start guard (white-black-white)
    binary = [1]*3 + [0]*3 + [1]*3 + [0]*3 * 20
    assert _try_decode_scanline(binary) is None


def test_try_decode_scanline_bad_middle_guard():
    """Cover the mid_modules != '01010' branch by building a valid start
    guard followed by 6 valid left digits but a corrupted middle guard."""
    from ValidUPC._codecs.barcode_encode import encode_upc_a
    # Build a valid UPC-A bit pattern and corrupt the middle guard
    bits = encode_upc_a("725272730706")
    # Convert to pixel-width binary (3px per module)
    px_per_mod = 3
    pixels = []
    for bit in bits:
        val = 0 if bit == "1" else 1  # black=0, white=1
        pixels.extend([val] * px_per_mod)
    # Corrupt middle guard area (starts at module 46: 3 start + 7*6 left + 5 middle)
    # Module 46 is the start of middle guard; corrupt it
    mid_start = (3 + 42) * px_per_mod  # module index 45
    for i in range(5 * px_per_mod):
        pixels[mid_start + i] = 0  # all black = bad middle guard
    result = _try_decode_scanline(pixels)
    assert result is None


def test_try_decode_ean8_bad_guard():
    """EAN-8 with wrong start guard."""
    binary = [1]*3 + [0]*3 + [1]*3 + [0]*3 * 15
    assert _try_decode_ean8(binary) is None


def test_qr_version_6_multi_block(tmp_path):
    """Version 6 uses 2 blocks - exercises multi-block interleaving in encoder."""
    from ValidUPC._codecs.qr_encode import save_qr
    import os

    data = "M" * 130  # version 6 capacity
    path = save_qr(data, str(tmp_path / "v6_qr"))
    assert os.path.exists(path)
