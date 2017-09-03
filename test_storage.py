import unittest, os
from datetime import datetime, date
from scraping import date_short_format
import scrape_logger
from scraping import datetime_format

import storage


level = "WARNING"
#level = "INFO"
#level = "DEBUG"
logger = scrape_logger.setup_logger(level)


storage_directory = "scrapes"
names_filename_all = "test\\names_test_all.tsv"


class Test(unittest.TestCase):

    def test_store_names(self):
        filename_temp = "test\\names_temp.tsv"
        company_names = {1:"a", 2:"b", 2048:"talenom"}
        storage.store_names(storage_directory, company_names,
                            names_filename=filename_temp)

        company_names_loaded = storage.load_names(filename_temp)
        self.assertDictEqual(company_names, company_names_loaded)

        os.remove(filename_temp)

    def test_load__names(self):
        company_names = storage.load_names(names_filename_all)

        self.assertEqual(len(company_names), 157)
        self.assertIsInstance(company_names, dict)
        for company_id in company_names:
            self.assertIsInstance(company_id, int)
            self.assertIsInstance(company_names[company_id], str)

    def test_get_latest_metrics_filename(self):
        # Create empty file with an old filename.
        old_filename = storage_directory + "\\metrics_15-12-31_23-59-50.json"
        f = open(old_filename, "w")
        f.close()
        self.assertTrue(os.path.isfile(old_filename))

        # Create empty file with an wrong filename.
        wrong_filename = storage_directory + "\\metrics_1512.json"
        f = open(wrong_filename, "w")
        f.close()
        self.assertTrue(os.path.isfile(wrong_filename))

        # Create empty file with filename like a newly created metrics file.
        expected_filename = storage_directory + "\\metrics_{}.json".format(
            datetime.now().strftime(datetime_format)
        )
        f = open(expected_filename, "w")
        f.close()
        self.assertTrue(os.path.isfile(expected_filename))

        filename = storage.get_latest_metrics_filename(storage_directory)
        os.remove(old_filename)
        os.remove(wrong_filename)
        os.remove(expected_filename)
        self.assertEqual(filename, expected_filename)

    def test_get_latest_metrics_filename_None(self):
        # Create empty temprorary directory.
        temp_empty_path = "test\\temp"
        self.assertFalse(os.path.exists(temp_empty_path))
        os.makedirs(temp_empty_path)

        filename = storage.get_latest_metrics_filename(temp_empty_path)
        os.rmdir(temp_empty_path)
        self.assertEqual(filename, None)

    def test_load_todays_names(self):
        # remove all names files from today
        date_str = date.today().strftime(date_short_format) # YY-MM-DD
        filename_start_today = "names_{}".format(date_str)
        files = os.listdir(storage_directory)
        for filename in files:
            if filename.startswith(filename_start_today):
                full_filename = storage_directory +'\\'+ filename
                os.remove(full_filename)
        company_names_empty = storage.load_todays_names(
            storage_directory
        )
        self.assertEqual(company_names_empty, None)

        # create company names file for today
        company_names = storage.load_names(names_filename_all)
        filename_today = storage.store_names(
            storage_directory, company_names
        )

        company_names_loaded = storage.load_todays_names(
            storage_directory
        )
        self.assertDictEqual(company_names, company_names_loaded)

        os.remove(filename_today)

    def test_store_metrics(self):
        metrics_filename_temp = "test\\metrics_temp.json"
        metrics_list = [
            {"company_id": 1, "company_name": "foo"},
            {"company_id": 2, "company_name": "bar", "val": "hello"}
        ]
        expected_str = '{"metrics": [' + \
            '{"company_id": 1,"company_name": "foo"},' + \
            '{"company_id": 2,"company_name": "bar","val": "hello"}]}'
        storage.store_metrics(storage_directory, metrics_list,
                              metrics_filename_temp)

        line = True
        s = ""
        with open(metrics_filename_temp, "r") as f:
            while line: 
                line = f.readline().strip()
                s += line

        self.assertEqual(s, expected_str)

        os.remove(metrics_filename_temp)

    def test_load_metrics(self):
        metrics_filename = "test\\metrics_test1.json"
        metrics_list = storage.load_metrics(metrics_filename)

        self.assertIsInstance(metrics_list, list)
        self.assertGreater(len(metrics_list), 100)
        for metrics in metrics_list:
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 1)
            self.assertIsInstance(metrics["company_id"], int)
            self.assertIsInstance(metrics["company_name"], str)


if __name__ == '__main__':
    unittest.main()
