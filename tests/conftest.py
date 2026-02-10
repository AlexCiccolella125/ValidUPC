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
