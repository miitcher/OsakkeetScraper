import unittest, logging, os
from threading import Thread, Lock, Semaphore

import scraping
import scrapeKL


SHOW_DEBUG = True

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if not SHOW_DEBUG:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"

storage_directory = "scrapes"


class Test(unittest.TestCase):

    def test_scrape_and_store_companies_as_thread(self):
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma"
        }
        """
        company_names = {}
        """
        company_list = []
        company_failed_count = 0
        c_failed_semaphore_counter = Semaphore(value=0)
        filename_metrics = ""
        scrapeThread = Thread(
            target=scrapeKL.scrape_and_store_companies,
            args=(storage_directory, company_names, company_list,
                  company_failed_count, filename_metrics)
        )
        monitoringThread = Thread(
            target=scrapeKL.monitor_scraping,
            args=(company_names, company_list, company_failed_count)
        )

        monitoringThread.start()
        scrapeThread.start()
        scrapeThread.join()
        monitoringThread.join()

        self.assertIsInstance(filename_metrics, str)
        self.assertEqual(len(company_list), 3)
        for company in company_list:
            self.assertIsInstance(company, scraping.Company)
            self.assertIsInstance(company.json_metrics, str)
            self.assertGreater(len(company.json_metrics), 1000)


    """
    def test_scrape_companies_One_OLD(self):
        filename = scrapeKL.scrape_companies(storage_directory, {2048:"talenom"})
        self.assertTrue(os.path.isfile(filename))

        output_str = scrapeKL.print_companies(filename, return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrapeKL.print_company_metrics(filename, "metrics", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrapeKL.print_company_metrics(filename, "metrics_simple", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrapeKL.print_company_metrics(filename, "calculations", return_output=True)
        self.assertGreater(len(output_str), 0)
        # TODO: Better validation of print output.

        os.remove(filename)
    """


if __name__ == '__main__':
    unittest.main()
