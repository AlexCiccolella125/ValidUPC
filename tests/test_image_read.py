import pytest
from ValidUPC.UPC import Barcode, BarcodeType
from ValidUPC.image_gen import generate_barcode_image, generate_qr_image
from ValidUPC.image_read import read_barcode_image, read_qr_image


def test_read_upc_a_image(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.UPC_A]
    path = generate_barcode_image(bc, str(tmp_path / "upc_a"))
    results = read_barcode_image(path)
    assert len(results) >= 1
    assert any(r.code == bc.code for r in results)


def test_read_ean_13_image(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.EAN_13]
    path = generate_barcode_image(bc, str(tmp_path / "ean_13"))
    results = read_barcode_image(path)
    assert len(results) >= 1
    assert any(r.code == bc.code for r in results)


def test_read_ean_8_image(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.EAN_8]
    path = generate_barcode_image(bc, str(tmp_path / "ean_8"))
    results = read_barcode_image(path)
    assert len(results) >= 1
    assert any(r.code == bc.code for r in results)


def test_read_qr_image(tmp_path):
    data = "Hello, QR Code!"
    path = generate_qr_image(data, str(tmp_path / "qr"))
    results = read_qr_image(path)
    assert len(results) == 1
    assert results[0].data == data


def test_read_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        read_barcode_image("/tmp/nonexistent_barcode.png")
