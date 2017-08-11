import unittest, logging, os
from datetime import date
from scraping import date_short_format, Company

import storage


SHOW_DEBUG = False

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if not SHOW_DEBUG:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)


storage_directory = "scrapes"


class Test(unittest.TestCase):

    def test_load_company_names(self):
        filename = "test\\scrape_names_test.tsv"
        company_names = storage._load_company_names(filename)

        self.assertEqual(len(company_names), 157)
        self.assertIsInstance(company_names, dict)
        for company_id in company_names:
            self.assertIsInstance(company_id, int)
            self.assertIsInstance(company_names[company_id], str)

    def test_load_todays_company_names(self):
        # remove all scrape_names files from today
        date_str = date.today().strftime(date_short_format) # YY-MM-DD
        filename_start_today = "scrape_names_{}".format(date_str)
        files = os.listdir(storage_directory)
        for filename in files:
            if filename.startswith(filename_start_today):
                full_filename = storage_directory +'\\'+ filename
                os.remove(full_filename)
        company_names_empty = storage.load_todays_company_names(storage_directory)
        self.assertEqual(company_names_empty, None)

        # create company names file for today
        company_names = {1:"a", 2:"b", 2048:"talenom"}
        filename_today = storage.store_company_names(company_names, storage_directory)

        company_names_loaded = storage.load_todays_company_names(storage_directory)
        self.assertDictEqual(company_names, company_names_loaded)

        os.remove(filename_today)

    def test_load_company_list(self):
        # TODO: When the right format for metrics is done, then this can be implemented.
        pass

    def test_store_company_names(self):
        filename_temp = "test\\scrape_names_temp.tsv"
        company_names = {1:"a", 2:"b", 2048:"talenom"}
        storage.store_company_names(company_names, storage_directory, filename=filename_temp)

        company_names_loaded = storage._load_company_names(filename_temp)
        self.assertDictEqual(company_names, company_names_loaded)

        os.remove(filename_temp)

    def test_store_company_list(self):
        # TODO: When the right format for metrics is done, then this can be implemented.
        pass

    def test_store_company_data_invalid(self):
        # invalid scrape_type
        self.assertRaises(AssertionError, storage._store_company_data, None, storage_directory, "foo")
        # invalid company_data
        self.assertRaises(AssertionError, storage._store_company_data, [1], storage_directory, "names")
        self.assertRaises(AssertionError, storage._store_company_data, {"1":"name"}, storage_directory, "names")
        self.assertRaises(AssertionError, storage._store_company_data, {1:2}, storage_directory, "names")
        self.assertRaises(AssertionError, storage._store_company_data, [1], storage_directory, "metrics")
        self.assertRaises(AssertionError, storage._store_company_data, [Company(c_id=1, c_name="bar")], storage_directory, "metrics")


if __name__ == '__main__':
    unittest.main()
