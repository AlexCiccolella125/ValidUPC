import argparse
import sys
from ValidUPC.UPC import validate_upc

def parse_args():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    ap.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    ap.add_argument(
        "-d",
        "--duplicates",
        action="store_true",
        help="signals to output duplicates",
    )

    return ap.parse_args()

def main():
    args = parse_args()
    print(args)
    if '.txt' in args.infile.name:
        barcodes = [line.strip() for line in args.infile.readlines()]
        pass

    elif '.csv' in args.infile.name:
        barcodes = [line.strip() for line in str(args.infile.read()).split('\n') if line]
        print(barcodes)
    else:
        print("not txt or csv")
    
    for barcode in barcodes:
        
        print(f"{barcode} {validate_upc(barcode)}")
        
    # print(args.infile.read())
    print(args.infile.name)

if __name__ == "__main__":
    main()