# algorithm description source: https://www.ibm.com/docs/en/zos/2.3.0?topic=parameters-check-digit-calculation-method

# with open("barcodes.txt") as f:
#     barcodes = [line.strip() for line in f.readlines()]

# duplicates = set(x for x in barcodes if barcodes.count(x) > 1)

# with open("duplicates.txt", "w") as f:
#     for duplicate in duplicates:
#         f.write(duplicate + "\n")


# class UPC:

#     def __init__(self, *, filepath='', duplicates='') -> None:
#         self.filepath = filepath
#         self.duplicates = duplicates

def validate_upc(code:int) -> bool:
    digits = str(code)
    return int(digits[-1]) == generate_checkdigit(int(digits[:-1]))

def generate_checkdigit(code:int) -> int:
    digits = [int(d) for d in str(code)]
    for i in range(0, len(digits), 2):
        digits[i] *= 3
    checkdigit = (10 - (sum(digits) % 10)) % 10
    
    return checkdigit

        