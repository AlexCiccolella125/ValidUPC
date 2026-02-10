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


def test_read_ean_8_with_expected_type(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.EAN_8]
    path = generate_barcode_image(bc, str(tmp_path / "ean_8_typed"))
    results = read_barcode_image(path, expected_type=BarcodeType.EAN_8)
    assert len(results) >= 1
    assert any(r.code == bc.code for r in results)


def test_read_barcode_wrong_expected_type(tmp_path, sample_barcodes):
    bc = sample_barcodes[BarcodeType.UPC_A]
    path = generate_barcode_image(bc, str(tmp_path / "upc_a_wrong"))
    with pytest.raises(ValueError):
        read_barcode_image(path, expected_type=BarcodeType.EAN_8)


def test_read_blank_image_no_barcodes(tmp_path):
    from PIL import Image
    blank = Image.new("L", (100, 100), 255)
    path = str(tmp_path / "blank.png")
    blank.save(path)
    with pytest.raises(ValueError, match="No barcodes found"):
        read_barcode_image(path)


def test_read_blank_image_no_qr(tmp_path):
    from PIL import Image
    blank = Image.new("L", (100, 100), 255)
    path = str(tmp_path / "blank_qr.png")
    blank.save(path)
    with pytest.raises(ValueError, match="No QR codes found"):
        read_qr_image(path)


def test_read_barcode_filters_unknown_type(tmp_path, monkeypatch):
    """Cover the continue when barcode_type is None (unknown type string)."""
    from ValidUPC import image_read
    monkeypatch.setattr(
        image_read, "decode_barcode_from_image",
        lambda path: [{"code_str": "12345", "barcode_type": "UNKNOWN"}],
    )
    monkeypatch.setattr(
        image_read, "decode_ean8_from_image",
        lambda path: [],
    )
    with pytest.raises(ValueError, match="No valid barcodes"):
        read_barcode_image(str(tmp_path / "dummy.png"))


def test_read_barcode_filters_mismatched_type(tmp_path, monkeypatch):
    """Cover the continue when expected_type doesn't match decoded type."""
    from ValidUPC import image_read
    monkeypatch.setattr(
        image_read, "decode_barcode_from_image",
        lambda path: [{"code_str": "725272730706", "barcode_type": "UPC_A"}],
    )
    monkeypatch.setattr(
        image_read, "decode_ean8_from_image",
        lambda path: [],
    )
    with pytest.raises(ValueError, match="No valid barcodes"):
        read_barcode_image(str(tmp_path / "dummy.png"), expected_type=BarcodeType.EAN_13)


def test_read_barcode_skips_invalid_code(tmp_path, monkeypatch):
    """Cover the ValueError continue when Barcode() validation fails."""
    from ValidUPC import image_read
    monkeypatch.setattr(
        image_read, "decode_barcode_from_image",
        lambda path: [{"code_str": "000000000001", "barcode_type": "UPC_A"}],
    )
    monkeypatch.setattr(
        image_read, "decode_ean8_from_image",
        lambda path: [],
    )
    with pytest.raises(ValueError, match="No valid barcodes"):
        read_barcode_image(str(tmp_path / "dummy.png"))


def test_read_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        read_barcode_image("/tmp/nonexistent_barcode.png")
