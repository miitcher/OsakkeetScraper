import unittest
import scrape_logger
import storage

import processing


import json


level = "WARNING"
#level = "INFO"
#level = "DEBUG"
logger = scrape_logger.setup_logger(level)


test_filenames = [
    "test\\metrics_test_2048.json"
]


class Test(unittest.TestCase):

    def test_Processing_smoketest(self):
        filename = "test\\metrics_test_all.json"
        metrics_list = storage.load_metrics(filename)
        for metrics in metrics_list:
            processor = processing.Processor(metrics)
            collection = processor.process()
            #print(json.dumps(metrics, indent=3))
            self.assertIsInstance(collection, dict)
            self.assertEqual(len(collection), 16)

    def test_get_tulostiedot_key(self):
        # TODO: Good to test, so I do not need to think of it later.
        pass

    def test_collect_and_calculate_metrics(self):
        for filename in test_filenames:
            test_collect_and_calculate_metrics_Controll(self, filename)

    def test_filter(self):
        for filename in test_filenames:
            test_filter_Controll(self, filename)


def test_collect_and_calculate_metrics_Controll(tester, filename):
    metrics = storage.load_metrics(filename)[0]
    #print(json.dumps(metrics, indent=3))

    processor = processing.Processor(metrics)
    collection = processor.collect_and_calculate_metrics()

    #print(json.dumps(collection, indent=3))
    tester.assertEqual(len(collection), 15)
    # TODO: add more asserting

def test_filter_Controll(tester, filename):
    metrics = storage.load_metrics(filename)[0]
    #print(json.dumps(metrics, indent=3))

    processor = processing.Processor(metrics)
    collection = processor.process()

    #print(json.dumps(collection, indent=3))
    tester.assertEqual(len(collection), 16)
    # TODO: add more asserting

if __name__ == '__main__':
    unittest.main()
