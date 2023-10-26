import unittest
from ValidUPC.UPC import validate_upc, generate_checkdigit

class TestCheckdigit(unittest.TestCase):
    def test_generate_checkdigit(self):
        # testing known valid UPC codes UPC-A
        self.assertEqual(generate_checkdigit(72527273070), 6)
        self.assertEqual(generate_checkdigit(12345678910), 4)

        # testing known valid UPC codes EAN-8
        self.assertEqual(generate_checkdigit(9031101), 7)

        # testing known valid UPC codes EAN-13
        self.assertEqual(generate_checkdigit(978044137962), 0)

        # testing known valid UPC codes EAN-14
        self.assertEqual(generate_checkdigit(1845678901001), 0)



    def test_validate_upc(self):
        # testing known valid UPC codes UPC-A
        self.assertTrue(validate_upc(725272730706))
        self.assertTrue(validate_upc(123456789104))
        self.assertFalse(validate_upc(123456789105))


        # testing known valid UPC codes EAN-8
        self.assertTrue(validate_upc(90311017))
        self.assertFalse(validate_upc(90311018))

        # testing known valid UPC codes EAN-13
        self.assertTrue(validate_upc(9780441379620))
        self.assertFalse(validate_upc(9780441379629))
        

        # testing known valid UPC codes EAN-14
        self.assertTrue(validate_upc(18456789010010))
        self.assertFalse(validate_upc(18456789010018))


if __name__ == '__main__':
    unittest.main()