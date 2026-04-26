import unittest

from core.utils import mask_sensitive_id


class UtilsTests(unittest.TestCase):
    def test_mask_sensitive_id_hides_middle_digits(self):
        self.assertEqual(mask_sensitive_id(9876543210), "987***210")

    def test_mask_sensitive_id_handles_short_values(self):
        self.assertEqual(mask_sensitive_id(1234), "****")


if __name__ == "__main__":
    unittest.main()
