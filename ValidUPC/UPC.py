# algorithm description source: https://www.ibm.com/docs/en/zos/2.3.0?topic=parameters-check-digit-calculation-method
from enum import Enum
from dataclasses import dataclass

class BarcodeType(Enum):
    UPC_A = 'UPC-A'
    UPC_E = 'UPC-E'
    EAN_8 = 'EAN-8'
    EAN_13 = 'EAN-13'

@dataclass(kw_only=True, slots=True)
class Barcode:
    code: int
    type: BarcodeType 
    checkdigit: bool = False

    def __post_init__(self):
        if self.checkdigit:
            self.code = (code * 10) + generate_checkdigit(self.code)

        if not isinstance(self.type, BarcodeType):
            raise ValueError('type must be an instance of BarcodeType')

        match (self.type, self.code):
            # UPC-A should have 12 digits with checkdigit
            case ['UPC_A', code] if len(str(code)) == 12:
                if not validate_upc(code):
                    print("UPC-A is invalid")
                    raise ValueError("UPC-A is invalid")

            # # UPC-E should have 8 digits with checkdigit
            # case [type, code] if type == "UPC-E" and len(str(code)) == 8:
            #     if not validate_upc(code):
            #         print("UPC-E is invalid")
            #         raise ValueError("UPC-E is invalid")
                
            # case [type, code] if type == "EAN-8" and len(str(code)) == 8:
            #     if not validate_upc(code):
            #         print("EAN-8 is invalid")
            #         raise ValueError("EAN-8 is invalid")

            # case [type, code] if type == "EAN-13" and len(str(code)) == 13:
            #     if not validate_upc(code):
            #         print("EAN-13 is invalid")
            #         raise ValueError("EAN-13 is invalid")
                



def validate_upc(code) -> bool:
    digits = str(code)
    try:
        code = int(digits[-1])
        check = generate_checkdigit(int(digits[:-1]))
        return code == check

    except ValueError:
        # pass
        print("failed")
        return False
    except IndexError:
        # pass
        print("failed")
        return False


def generate_checkdigit(code: int) -> int:
    digits = [int(d) for d in str(code)]
    for i in range(0, len(digits), 2):
        digits[i] *= 3
    checkdigit = (10 - (sum(digits) % 10)) % 10

    return checkdigit
