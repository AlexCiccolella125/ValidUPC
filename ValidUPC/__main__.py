import argparse
import sys
import re
from ValidUPC.UPC import BarcodeType, Barcode


def parse_args():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("-i", "--infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    ap.add_argument(
        "-o", "--outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    ap.add_argument(
        "-e","--errfile", nargs="?", type=argparse.FileType("w"), default=sys.stderr
    )
    ap.add_argument(
        "-t",
        "--type_of_barcode",
        help="Define the type of barcode to validate",
        default="UPC_A",
        nargs=1,
    )
    
    ap.add_argument(
        "-v",
        "--verbose",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Verbose output, does not go to outfile",
    )

    return ap.parse_args()


def main():
    args = parse_args()

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


if __name__ == "__main__":
    main()
