import pytest
from ValidUPC.UPC import Barcode, BarcodeType
from ValidUPC.image_gen import generate_barcode_image, generate_qr_image
from ValidUPC.image_read import read_barcode_image, read_qr_image


@pytest.mark.parametrize("barcode_type,code", [
    (BarcodeType.UPC_A, 725272730706),
    (BarcodeType.UPC_A, 123456789104),
    (BarcodeType.EAN_8, 90311017),
    (BarcodeType.EAN_13, 9780441379620),
])
def test_roundtrip(tmp_path, barcode_type, code):
    """Generate a barcode image, then read it back and verify the code matches."""
    original = Barcode(code=code, type=barcode_type)

    # Generate
    image_path = generate_barcode_image(original, str(tmp_path / "roundtrip"))

    # Read back
    results = read_barcode_image(image_path)

    # Verify the original code appears in decoded results
    decoded_codes = [r.code for r in results]
    assert original.code in decoded_codes, (
        f"Expected {original.code} in decoded results, got {decoded_codes}"
    )


@pytest.mark.parametrize("data", [
    "https://example.com",
    "Hello, World!",
    "1234567890",
])
def test_roundtrip_qr(tmp_path, data):
    """Generate a QR code image, then read it back and verify the data matches."""
    image_path = generate_qr_image(data, str(tmp_path / "qr_roundtrip"))
    results = read_qr_image(image_path)
    decoded_data = [r.data for r in results]
    assert data in decoded_data, (
        f"Expected '{data}' in decoded results, got {decoded_data}"
    )
