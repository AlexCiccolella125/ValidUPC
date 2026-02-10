from ValidUPC.UPC import Barcode, BarcodeType
from ValidUPC._codecs.barcode_encode import (
    encode_upc_a, encode_ean_8, encode_ean_13, render_barcode,
)

_ENCODERS = {
    BarcodeType.UPC_A: encode_upc_a,
    BarcodeType.EAN_8: encode_ean_8,
    BarcodeType.EAN_13: encode_ean_13,
}


def generate_barcode_image(barcode_obj: Barcode, output_path: str,
                           image_format: str = "png") -> str:
    """Generate a barcode image file from a validated Barcode object.

    Args:
        barcode_obj: A validated Barcode instance.
        output_path: Path for the output file (without extension).
        image_format: "png" or "svg".

    Returns:
        The full path of the generated file (extension appended).

    Raises:
        ValueError: If the barcode type is not supported for image generation.
    """
    encoder = _ENCODERS.get(barcode_obj.type)
    if encoder is None:
        raise ValueError(
            f"{barcode_obj.type.name} image generation is not supported"
        )

    code_str = str(barcode_obj.code).zfill(barcode_obj.type.value)
    bit_pattern = encoder(code_str)
    return render_barcode(bit_pattern, output_path, image_format)


def generate_qr_image(data: str, output_path: str) -> str:
    """Generate a QR code image from arbitrary text data.

    Args:
        data: The text to encode in the QR code.
        output_path: Path for the output file (without extension).

    Returns:
        The full path of the generated PNG file.
    """
    from ValidUPC._codecs.qr_encode import save_qr
    return save_qr(data, output_path)
