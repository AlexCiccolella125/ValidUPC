import argparse
import sys
import re
from ValidUPC.UPC import BarcodeType, Barcode


def parse_args():
    ap = argparse.ArgumentParser(
        prog="ValidUPC",
        description="Validate, generate, and read barcodes",
        allow_abbrev=False,
    )
    subparsers = ap.add_subparsers(dest="command")

    # --- validate subcommand ---
    val = subparsers.add_parser("validate", help="Validate barcodes from file/stdin")
    val.add_argument(
        "-i", "--infile", nargs="?",
        type=argparse.FileType("r"), default=sys.stdin,
    )
    val.add_argument(
        "-o", "--outfile", nargs="?",
        type=argparse.FileType("w"), default=sys.stdout,
    )
    val.add_argument(
        "-e", "--errfile", nargs="?",
        type=argparse.FileType("w"), default=sys.stderr,
    )
    val.add_argument(
        "-t", "--type_of_barcode",
        help="Define the type of barcode to validate",
        default="UPC_A", nargs=1,
    )
    val.add_argument(
        "-v", "--verbose", default=False,
        action=argparse.BooleanOptionalAction,
        help="Verbose output, does not go to outfile",
    )

    # --- generate subcommand ---
    gen = subparsers.add_parser("generate", help="Generate a barcode image")
    gen.add_argument(
        "-c", "--code", required=True,
        help="Barcode number (digits) or text data (for QR)",
    )
    gen.add_argument(
        "-t", "--type_of_barcode",
        default="UPC_A",
        help="Barcode type (UPC_A, EAN_8, EAN_13, QR)",
    )
    gen.add_argument(
        "-o", "--output", default="barcode",
        help="Output file path (without extension)",
    )
    gen.add_argument(
        "--format", choices=["png", "svg"], default="png",
        dest="image_format",
    )

    # --- read subcommand ---
    rd = subparsers.add_parser("read", help="Read a barcode from an image")
    rd.add_argument(
        "-i", "--image", required=True,
        help="Path to barcode image",
    )
    rd.add_argument(
        "-t", "--type_of_barcode", default=None,
        help="Expected barcode type (UPC_A, EAN_8, EAN_13, QR)",
    )

    return ap.parse_args()


def cmd_validate(args):
    if args.verbose:
        print("reading file")

    barcodes = [
        line.strip() for line in re.split("\n|,", str(args.infile.read())) if line
    ]

    if args.verbose:
        print(f"{len(barcodes)} barcodes found")

    if args.verbose:
        print("validating barcodes")

    for barcode in barcodes:
        try:
            args.outfile.write(
                str(Barcode(code=int(barcode), type=BarcodeType[args.type_of_barcode]))
                + "\n"
            )
        except ValueError:
            args.errfile.write(f"Invalid {args.type_of_barcode}: {barcode}\n")
            continue


def cmd_generate(args):
    if args.type_of_barcode == "QR":
        from ValidUPC.image_gen import generate_qr_image
        path = generate_qr_image(args.code, args.output)
    else:
        from ValidUPC.image_gen import generate_barcode_image
        barcode_type = BarcodeType[args.type_of_barcode]
        barcode_obj = Barcode(code=int(args.code), type=barcode_type)
        path = generate_barcode_image(barcode_obj, args.output, args.image_format)
    print(f"Generated image: {path}")


def cmd_read(args):
    if args.type_of_barcode == "QR":
        from ValidUPC.image_read import read_qr_image
        results = read_qr_image(args.image)
        for qr in results:
            print(f"QR: {qr.data}")
    else:
        from ValidUPC.image_read import read_barcode_image
        expected_type = BarcodeType[args.type_of_barcode] if args.type_of_barcode else None
        results = read_barcode_image(args.image, expected_type)
        for bc in results:
            code_str = str(bc.code).zfill(bc.type.value)
            print(f"{bc.type.name}: {code_str}")


def main():
    args = parse_args()

    if args.command is None:
        print("Usage: ValidUPC {validate,generate,read} ...")
        print("Run 'ValidUPC -h' for help.")
        sys.exit(1)

    match args.command:
        case "validate":
            cmd_validate(args)
        case "generate":
            cmd_generate(args)
        case "read":
            cmd_read(args)


if __name__ == "__main__":
    main()
