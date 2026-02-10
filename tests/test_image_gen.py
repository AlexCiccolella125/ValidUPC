import os
import pytest
from ValidUPC.UPC import Barcode, BarcodeType
from ValidUPC.image_gen import generate_barcode_image, generate_qr_image


def test_generate_upc_a_image(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.UPC_A]
    path = generate_barcode_image(bc, str(tmp_path / "upc_a"))
    assert os.path.exists(path)
    assert path.endswith(".png")


def test_generate_ean_8_image(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.EAN_8]
    path = generate_barcode_image(bc, str(tmp_path / "ean_8"))
    assert os.path.exists(path)
    assert path.endswith(".png")


def test_generate_ean_13_image(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.EAN_13]
    path = generate_barcode_image(bc, str(tmp_path / "ean_13"))
    assert os.path.exists(path)
    assert path.endswith(".png")


def test_generate_svg_format(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.UPC_A]
    path = generate_barcode_image(bc, str(tmp_path / "upc_a_svg"), image_format="svg")
    assert os.path.exists(path)
    assert path.endswith(".svg")


def test_generate_upc_e_raises():
    bc = Barcode(code=1234561, type=BarcodeType.UPC_E)
    with pytest.raises(ValueError, match="UPC_E.*not supported"):
        generate_barcode_image(bc, "/tmp/should_not_exist")


def test_generate_qr_image(tmp_path):
    path = generate_qr_image("https://example.com", str(tmp_path / "qr"))
    assert os.path.exists(path)
    assert path.endswith(".png")
