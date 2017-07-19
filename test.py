"""
cd /c/Eclipse\ workspace/OsakkeetScraper
python -m unittest -v
"""
import unittest
from scraping import *
from scrape_KL import *


class Test_scraping(unittest.TestCase):

    def test_scrape_company2(self):
        self.assertEqual(3,3)

    def test_scrape_company4(self):
        self.assertEqual(3,3)


class Test_scrape_KL(unittest.TestCase):

    def test_scrape_KL(self):
        self.assertEqual(3,3)


if __name__ == '__main__':
    unittest.main()