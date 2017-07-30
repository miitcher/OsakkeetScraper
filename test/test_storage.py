import unittest, logging

fast_tests = True
show_debug = False

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if not show_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

import storage


storage_directory = "scrapes"


class Test_storage(unittest.TestCase):

    def test_load_todays_company_names(self):
        pass

    def test_load_company_list(self):
        pass

    def test_store_company_data(self):
        pass


if __name__ == '__main__':
    unittest.main()
