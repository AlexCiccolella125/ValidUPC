import barcode
from barcode.writer import ImageWriter
import qrcode
from ValidUPC.UPC import Barcode, BarcodeType, BARCODE_FORMAT_MAP


def generate_barcode_image(barcode_obj: Barcode, output_path: str,
                           image_format: str = "png") -> str:
    """Generate a barcode image file from a validated Barcode object.

    Args:
        barcode_obj: A validated Barcode instance.
        output_path: Path for the output file (without extension).
        image_format: "png" or "svg".

    Returns:
        The full path of the generated file (extension appended by library).

    Raises:
        ValueError: If the barcode type is not supported for image generation.
    """
    fmt = BARCODE_FORMAT_MAP.get(barcode_obj.type)
    if fmt is None:
        raise ValueError(
            f"{barcode_obj.type.name} image generation is not supported"
        )

    # Zero-pad to correct length, then strip check digit (library recomputes it)
    code_str = str(barcode_obj.code).zfill(barcode_obj.type.value)[:-1]

    writer = ImageWriter() if image_format == "png" else None
    bc = barcode.get(fmt, code_str, writer=writer)
    return bc.save(output_path)


def generate_qr_image(data: str, output_path: str) -> str:
    """Generate a QR code image from arbitrary text data.

    Args:
        data: The text to encode in the QR code.
        output_path: Path for the output file (without extension).

    Returns:
        The full path of the generated PNG file.
    """
    img = qrcode.make(data)
    full_path = output_path + ".png"
    img.save(full_path)
    return full_path
