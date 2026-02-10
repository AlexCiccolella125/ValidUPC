from dataclasses import dataclass
from PIL import Image
from pyzbar.pyzbar import decode
from ValidUPC.UPC import Barcode, BarcodeType, PYZBAR_TYPE_MAP


@dataclass
class QRResult:
    data: str


def read_barcode_image(image_path: str,
                       expected_type: BarcodeType = None) -> list[Barcode]:
    """Read and decode barcodes from an image file.

    Args:
        image_path: Path to the barcode image file.
        expected_type: If provided, filter results to this type only.

    Returns:
        List of decoded and validated Barcode objects.

    Raises:
        FileNotFoundError: If image_path does not exist.
        ValueError: If no valid barcodes are found.
    """
    img = Image.open(image_path)
    decoded = decode(img)

    if not decoded:
        raise ValueError(f"No barcodes found in {image_path}")

    results = []
    for d in decoded:
        code_str = d.data.decode("utf-8")
        pyzbar_type = d.type

        barcode_type = PYZBAR_TYPE_MAP.get(pyzbar_type)

        # pyzbar often reports UPC-A as EAN-13 with a leading zero.
        # Since int() drops leading zeros, EAN-13 codes starting with 0
        # won't pass length validation, so treat them as UPC-A.
        if (barcode_type == BarcodeType.EAN_13
                and code_str.startswith("0")
                and len(code_str) == 13):
            barcode_type = BarcodeType.UPC_A
            code_str = code_str[1:]  # strip leading zero

        if barcode_type is None:
            continue

        if expected_type and barcode_type != expected_type:
            continue

        try:
            results.append(
                Barcode(code=int(code_str), type=barcode_type)
            )
        except ValueError:
            continue

    if not results:
        raise ValueError(f"No valid barcodes found in {image_path}")

    return results


def read_qr_image(image_path: str) -> list[QRResult]:
    """Read and decode QR codes from an image file.

    Args:
        image_path: Path to the QR code image file.

    Returns:
        List of QRResult objects containing decoded text.

    Raises:
        FileNotFoundError: If image_path does not exist.
        ValueError: If no QR codes are found.
    """
    img = Image.open(image_path)
    decoded = decode(img)

    results = [
        QRResult(data=d.data.decode("utf-8"))
        for d in decoded
        if d.type == "QRCODE"
    ]

    if not results:
        raise ValueError(f"No QR codes found in {image_path}")

    return results
