import unittest, os, time
import scrape_logger

import scrapeKL


level = "INFO"
#level = "DEBUG"
logger = scrape_logger.setup_logger(level)


storage_directory = "scrapes"


class Test(unittest.TestCase):

    def test_scrape_companies(self):
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma",
            1196: "afarak group"
        }
        #company_names = None # For scraping every company
        showProgress = False

        time0 = time.time()
        metrics_list, failed_company_dict, metricsfilename \
            = scrapeKL.scrape_companies(
                storage_directory, company_names, showProgress
            )
        logger.debug("\nScraping time: {:.2f} s".format(time.time() - time0))

        self.assertIsInstance(metricsfilename, str)
        for metrics in metrics_list:
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 1)
            logger.debug("company_name: {}".format(metrics['company_name']))
        for company_id in failed_company_dict:
            logger.debug("Failed list: ({}, {})".format(
                company_id, failed_company_dict[company_id])
            )

        self.assertEqual(len(failed_company_dict), 0)
        self.assertEqual(len(metrics_list), 4)

        os.remove(metricsfilename)

    def test_print_names1(self):
        scrapeKL.print_names(storage_directory=storage_directory)

    def test_print_names2(self):
        names_filename = "test\\names_test1.tsv"
        scrapeKL.print_names(names_filename=names_filename)

    def test_print_names3(self):
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma",
            1196: "afarak group",
            9999: "foobar"
        }
        scrapeKL.print_names(company_names=company_names)

    def test_print_metrics_working(self):
        metrics_filename = "test\\metrics_test1.json"
        scrapeKL.print_metrics(metrics_filename, None, "cramo")

    def test_print_metrics_failed(self):
        metrics_filename = "test\\metrics_test1.json"
        scrapeKL.print_metrics(metrics_filename, 1081, None)

    def test_print_metrics_bank(self):
        metrics_filename = "test\\metrics_test1.json"
        scrapeKL.print_metrics(metrics_filename, None, "aktia")

    def test_print_calculations_working(self):
        metrics_filename = "test\\metrics_test1.json"
        scrapeKL.print_calculations(metrics_filename, 1902, None)

    def test_print_calculations_failed(self):
        metrics_filename = "test\\metrics_test1.json"
        scrapeKL.print_calculations(metrics_filename, None, "basware")

    def test_print_calculations_bank(self):
        metrics_filename = "test\\metrics_test1.json"
        scrapeKL.print_calculations(metrics_filename, None, "aktia")


if __name__ == '__main__':
    unittest.main()
