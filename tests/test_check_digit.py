import pytest
from ValidUPC.UPC import validate_upc, generate_checkdigit, Barcode, BarcodeType


def test_generate_checkdigit():
    # testing known valid UPC codes UPC-A
    assert generate_checkdigit(72527273070) == 6
    assert generate_checkdigit(12345678910) == 4

    # testing known valid UPC codes EAN-8
    assert generate_checkdigit(9031101) == 7

    # testing known valid UPC codes EAN-13
    assert generate_checkdigit(978044137962) == 0


def test_validate_upc():
    # testing known valid UPC codes UPC-A
    assert validate_upc(725272730706)
    assert validate_upc(123456789104)
    assert not validate_upc(123456789105)

    # testing known valid UPC codes EAN-8
    assert validate_upc(90311017)
    assert not validate_upc(90311018)

    # testing known valid UPC codes EAN-13
    assert validate_upc(9780441379620)
    assert not validate_upc(9780441379629)


def test_barcode_creation():
    barcode = Barcode(type=BarcodeType.UPC_A, code="123456789012")
    assert barcode.type == BarcodeType.UPC_A
    assert barcode.code == "123456789012"


def test_invalid_barcode_type():
    with pytest.raises(ValueError):
        Barcode(type="InvalidType", code="123456789012")
        Barcode(type="UPC_A", code="19012")


if __name__ == "__main__":
    print(Barcode(type="InvalidType", code="19012"))
    pytest.main()
