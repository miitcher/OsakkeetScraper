""" https://docs.python.org/3.4/library/unittest.html """
import unittest, os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrape_KL import *


class Test_scrape_KL(unittest.TestCase):

    def test_scrape_company(self):
        self.assertEqual(3,3)


if __name__ == '__main__':
    unittest.main()