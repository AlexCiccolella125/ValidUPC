"""Tests using self-generated fixture images.

All fixture images are created by our own encoder at test time,
then decoded to verify the full encode-decode pipeline with a
variety of real barcode values.
"""
import pytest
from ValidUPC.UPC import BarcodeType
from ValidUPC.image_read import read_barcode_image, read_qr_image
from ValidUPC._codecs.barcode_decode import decode_barcode_from_image, decode_ean8_from_image
from ValidUPC._codecs.qr_decode import decode_qr_from_image


# --- UPC-A fixtures ---

@pytest.mark.parametrize("code", ["725272730706", "123456789104"])
def test_fixture_upca(generated_fixtures, code):
    path, expected, btype = generated_fixtures[f"upca_{code}"]
    decoded = decode_barcode_from_image(path)
    assert len(decoded) == 1
    assert decoded[0]["code_str"] == expected
    assert decoded[0]["barcode_type"] == "UPC_A"


@pytest.mark.parametrize("code", ["725272730706", "123456789104"])
def test_fixture_upca_validated(generated_fixtures, code):
    """Full pipeline: decode + Barcode validation."""
    path, expected, btype = generated_fixtures[f"upca_{code}"]
    results = read_barcode_image(path)
    assert len(results) >= 1
    assert results[0].code == int(expected)
    assert results[0].type == BarcodeType.UPC_A


# --- EAN-8 fixtures ---

@pytest.mark.parametrize("code", ["90311017", "55123457"])
def test_fixture_ean8(generated_fixtures, code):
    path, expected, btype = generated_fixtures[f"ean8_{code}"]
    decoded = decode_ean8_from_image(path)
    assert len(decoded) == 1
    assert decoded[0]["code_str"] == expected
    assert decoded[0]["barcode_type"] == "EAN_8"


@pytest.mark.parametrize("code", ["90311017", "55123457"])
def test_fixture_ean8_validated(generated_fixtures, code):
    path, expected, btype = generated_fixtures[f"ean8_{code}"]
    results = read_barcode_image(path, expected_type=BarcodeType.EAN_8)
    assert len(results) >= 1
    assert results[0].code == int(expected)
    assert results[0].type == BarcodeType.EAN_8


# --- EAN-13 fixtures ---

def test_fixture_ean13(generated_fixtures):
    path, expected, btype = generated_fixtures["ean13_9780441379620"]
    decoded = decode_barcode_from_image(path)
    assert len(decoded) == 1
    assert decoded[0]["code_str"] == expected
    assert decoded[0]["barcode_type"] == "EAN_13"


def test_fixture_ean13_validated(generated_fixtures):
    path, expected, btype = generated_fixtures["ean13_9780441379620"]
    results = read_barcode_image(path)
    assert len(results) >= 1
    assert results[0].code == int(expected)
    assert results[0].type == BarcodeType.EAN_13


# --- QR fixtures ---

@pytest.mark.parametrize("key,expected_data", [
    ("qr_Hello_World", "Hello World"),
    ("qr_https__example.com", "https://example.com"),
    ("qr_Test_1234!@#", "Test 1234!@#"),
])
def test_fixture_qr(generated_fixtures, key, expected_data):
    path, expected, btype = generated_fixtures[key]
    decoded = decode_qr_from_image(path)
    assert len(decoded) == 1
    assert decoded[0] == expected_data


@pytest.mark.parametrize("key,expected_data", [
    ("qr_Hello_World", "Hello World"),
    ("qr_https__example.com", "https://example.com"),
    ("qr_Test_1234!@#", "Test 1234!@#"),
])
def test_fixture_qr_validated(generated_fixtures, key, expected_data):
    """Full pipeline through read_qr_image."""
    path, expected, btype = generated_fixtures[key]
    results = read_qr_image(path)
    assert len(results) == 1
    assert results[0].data == expected_data
