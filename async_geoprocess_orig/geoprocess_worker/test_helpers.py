import unittest

import helpers

class TestGetProductSlugs(unittest.TestCase):

    def test_type(self):
        # https://stackabuse.com/python-check-if-variable-is-a-dictionary/
        s = helpers.get_product_slugs()
        self.assertIsInstance(s, dict)
    
    def test_response_not_empty(self):
        s = helpers.get_product_slugs()
        self.assertNotEqual(len(s), 0)


if __name__ == '__main__':
    unittest.main()
