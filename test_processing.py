import unittest, re
import scrape_logger
import storage

import processing


import json


level = "WARNING"
#level = "INFO"
#level = "DEBUG"
logger = scrape_logger.setup_logger(level)


filename_all = "test\\metrics_test_all.json"
test_filenames = [
    "test\\metrics_test_2048.json",
    "test\\metrics_test_2051.json"
]
test_expected_tulostiedot_key = [
    "2016-12-01",
    "2017-01-01"
]

date = re.compile("^\d{4}\-\d{2}\-\d{2}$") # YYYY-MM-DD


class Test(unittest.TestCase):

    def test_Processing_smoketest(self):
        metrics_list = storage.load_metrics(filename_all)
        for metrics in metrics_list:
            processor = processing.Processor(metrics)
            collection = processor.process()
            #print(json.dumps(metrics, indent=3))
            self.assertIsInstance(collection, dict)
            self.assertEqual(len(collection), 16)

    def test_get_tulostiedot_key_smoketest(self):
        metrics_list = storage.load_metrics(filename_all)
        for metrics in metrics_list:
            processor = processing.Processor(metrics)
            tulostiedot_key = processor.get_tulostiedot_key()
            if tulostiedot_key is not None:
                self.assertTrue(date.match(tulostiedot_key))
            #logger.warn(tulostiedot_key)

    def test_get_tulostiedot_key(self):
        i = 0
        for filename in test_filenames:
            test_get_tulostiedot_key_Controll(
                self, filename, test_expected_tulostiedot_key[i]
            )
            i += 1

    def test_get_tulostiedot_key_return_None(self):
        metrics_list = [
            {"kannattavuus": None},
            {"kannattavuus": "FAIL"}
        ]
        for metrics in metrics_list:
            processor = processing.Processor(metrics, fake_data=True)
            tulostiedot_key = processor.get_tulostiedot_key()
            self.assertEqual(tulostiedot_key, None)

    def test_collect_and_calculate_metrics(self):
        metrics_list = storage.load_metrics(filename_all)
        for metrics in metrics_list:
            #print(json.dumps(metrics, indent=3))
            test_collect_and_calculate_metrics_Controll(self, metrics)

    def test_filter(self):
        #filename_all = "test\\metrics_test_2048.json"
        metrics_list = storage.load_metrics(filename_all)
        for metrics in metrics_list:
            #print(json.dumps(metrics, indent=3))
            test_filter_Controll(self, metrics)

def test_get_tulostiedot_key_Controll(tester, filename, expected_date_str):
    metrics = storage.load_metrics(filename)[0]
    processor = processing.Processor(metrics)
    tulostiedot_key = processor.get_tulostiedot_key()
    tester.assertEqual(tulostiedot_key, expected_date_str)

def test_collect_and_calculate_metrics_Controll(tester, metrics):
    type_dict = {
        "tulostiedot_key": date,
        "osinko_tuotto_%": dict,
        "osinko_euro": dict,
        "steady_osinko": bool,
        "company_id": int,
        "company_name": str,
        "kurssi": float,
        "kuvaus": str,
        "scrape_date": date,
        "toimiala": str,
        "toimialaluokka": str,
        "osakkeet_kpl": int,
        "osinko_tuotto_%_fresh": float,
        "P_fresh": float,
        "needs_tulostiedot_key": dict
    }
    can_be_None = {
        "tulostiedot_key",
        "needs_tulostiedot_key",
        "toimiala",
        "toimialaluokka"
    }
    # Items in dicts are floats.

    processor = processing.Processor(metrics)
    collection = processor.collect_and_calculate_metrics()
    #logger.error(json.dumps(collection, indent=3))

    tester.assertEqual(len(collection), 15)
    for key in collection:
        if collection[key] is not None:
            if type_dict[key] == date:
                tester.assertTrue(date.match(collection[key]))
            elif type_dict[key] == dict:
                if key == "needs_tulostiedot_key" and collection[key]:
                    if collection[key]["P"]:
                        tester.assertEqual(len(collection[key]), 11)
                    else:
                        tester.assertEqual(len(collection[key]), 8)
                for k, v in collection[key].items():
                    if v is not None:
                        tester.assertTrue(
                            isinstance(v, float)
                            or isinstance(v, int)
                        )
                    elif key != "needs_tulostiedot_key":
                        logger.error(json.dumps(collection, indent=3))
                        raise AssertionError("{} can not be None".format(k))
            else:
                tester.assertIsInstance(collection[key], type_dict[key])
        elif key not in can_be_None:
            logger.error(json.dumps(collection, indent=3))
            raise AssertionError("{} can not be None".format(key))

def test_filter_Controll(tester, metrics):
    # skipped_filters can be a list or None.
    # The rest of the items in passed_filter are booleans.

    processor = processing.Processor(metrics)
    collection = processor.process()
    #logger.error(json.dumps(collection["passed_filter"], indent=3))

    tester.assertEqual(len(collection), 16)
    passed_filter = collection["passed_filter"]
    keys_list = []
    for key in passed_filter:
        keys_list.append(key)
        if key == "skipped_filters":
            skipped_filters = passed_filter["skipped_filters"]
            if skipped_filters is not None:
                tester.assertIsInstance(skipped_filters, list)
                for v in skipped_filters:
                    keys_list.append(v)
                    tester.assertIsInstance(v, str)
        else:
            tester.assertIsInstance(passed_filter[key], bool)
    tester.assertEqual(len(keys_list), 7)


if __name__ == '__main__':
    unittest.main()
