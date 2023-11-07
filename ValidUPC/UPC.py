# algorithm description source: https://www.ibm.com/docs/en/zos/2.3.0?topic=parameters-check-digit-calculation-method

def validate_upc(code:int) -> bool:
    digits = str(code)
    try: 
        code = int(digits[-1])
        check = generate_checkdigit(int(digits[:-1]))
        return  code == check

    except ValueError:
        # pass
        print("failed")
        return False
    except IndexError:
        # pass
        print("failed")
        return False

def generate_checkdigit(code:int) -> int:
    digits = [int(d) for d in str(code)]
    for i in range(0, len(digits), 2):
        digits[i] *= 3
    checkdigit = (10 - (sum(digits) % 10)) % 10
    
    return checkdigit

        