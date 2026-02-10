import os
import pytest
from ValidUPC.UPC import Barcode, BarcodeType


@pytest.fixture
def sample_barcodes():
    """Known-valid barcode objects for testing."""
    return {
        BarcodeType.UPC_A: Barcode(code=725272730706, type=BarcodeType.UPC_A),
        BarcodeType.EAN_8: Barcode(code=90311017, type=BarcodeType.EAN_8),
        BarcodeType.EAN_13: Barcode(code=9780441379620, type=BarcodeType.EAN_13),
    }


@pytest.fixture(scope="session")
def generated_fixtures(tmp_path_factory):
    """Generate barcode/QR fixture images using our own encoder.

    Returns a dict mapping descriptive names to (path, expected_value) tuples.
    Images are generated once per test session and shared across all tests.
    """
    from ValidUPC._codecs.barcode_encode import (
        encode_upc_a, encode_ean_8, encode_ean_13, render_barcode,
    )
    from ValidUPC._codecs.qr_encode import save_qr

    d = tmp_path_factory.mktemp("fixtures")
    fixtures = {}

    # UPC-A codes
    for code in ["725272730706", "123456789104"]:
        bits = encode_upc_a(code)
        path = render_barcode(bits, str(d / f"upca_{code}"), "png")
        fixtures[f"upca_{code}"] = (path, code, "UPC_A")

    # EAN-8 codes
    for code in ["90311017", "55123457"]:
        bits = encode_ean_8(code)
        path = render_barcode(bits, str(d / f"ean8_{code}"), "png")
        fixtures[f"ean8_{code}"] = (path, code, "EAN_8")

    # EAN-13 codes
    for code in ["9780441379620"]:
        bits = encode_ean_13(code)
        path = render_barcode(bits, str(d / f"ean13_{code}"), "png")
        fixtures[f"ean13_{code}"] = (path, code, "EAN_13")

    # QR codes
    for data in ["Hello World", "https://example.com", "Test 1234!@#"]:
        safe = data.replace("/", "_").replace(":", "").replace(" ", "_")
        path = save_qr(data, str(d / f"qr_{safe}"))
        fixtures[f"qr_{safe}"] = (path, data, "QR")

    return fixtures
