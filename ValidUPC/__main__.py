import argparse
import sys
# from ValidUpc import upc_a

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
        print("txt")
    elif '.csv' in args.infile.name:
        print("csv")
    else:
        print("not txt or csv")
    
        
    # print(args.infile.read())
    print(args.infile.name)

if __name__ == "__main__":
    main()