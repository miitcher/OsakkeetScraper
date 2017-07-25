import unittest, logging

import storage

skip_print_tests = False

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if skip_print_tests:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

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
