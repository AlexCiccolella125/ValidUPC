import argparse
import sys
import re
from ValidUPC.UPC import validate_upc, Barcode


def parse_args():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    ap.add_argument(
        "outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    ap.add_argument(
        "-t",
        "--type_of_barcode",
        action="store_true",
        help="Define the type of barcode to validate",
        default="UPC_A",
    )

    return ap.parse_args()


def main():
    args = parse_args()
    print(args)
    if ".txt" or ".csv" in args.infile.name:
        print("reading file")
        barcodes = [
            line.strip() for line in re.split("\n|,", str(args.infile.read())) if line
        ]

        print(f"{len(barcodes)} found \n{barcodes}")

        print("validating barcodes")
        for barcode in barcodes:
            print(f"{barcode} {validate_upc(barcode)}")

    else:
        print("not txt or csv")
