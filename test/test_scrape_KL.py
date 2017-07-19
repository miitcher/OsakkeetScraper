""" https://docs.python.org/3.4/library/unittest.html """
#import unittest, shutil, os, sys
import unittest
from scrape_KL import *


class Test_scrape_KL(unittest.TestCase):

    def test_one(self):
        self.assertEqual(3,3)

    def test_two(self):
        self.assertEqual(32,32)


if __name__ == '__main__':
    unittest.main()