from dataclasses import dataclass
from ValidUPC.UPC import Barcode, BarcodeType
from ValidUPC._codecs.barcode_decode import decode_barcode_from_image, decode_ean8_from_image

_TYPE_MAP = {
    "UPC_A": BarcodeType.UPC_A,
    "EAN_8": BarcodeType.EAN_8,
    "EAN_13": BarcodeType.EAN_13,
}


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
    # Try EAN-8 decoder if expected or as fallback
    if expected_type == BarcodeType.EAN_8:
        decoded = decode_ean8_from_image(image_path)
    else:
        decoded = decode_barcode_from_image(image_path)
        # Fallback to EAN-8 if nothing found
        if not decoded:
            decoded = decode_ean8_from_image(image_path)

    if not decoded:
        raise ValueError(f"No barcodes found in {image_path}")

    results = []
    for d in decoded:
        code_str = d["code_str"]
        barcode_type = _TYPE_MAP.get(d["barcode_type"])

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
    from ValidUPC._codecs.qr_decode import decode_qr_from_image

    decoded_strings = decode_qr_from_image(image_path)
    if not decoded_strings:
        raise ValueError(f"No QR codes found in {image_path}")
    return [QRResult(data=s) for s in decoded_strings]
