import unittest, logging, os, time

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


company_names = {
    2048: "talenom",
    1102: "cramo",
    1091: "sanoma"
}
company_names = {2048: "talenom"}
company_names = {1196: "afarak group"}
company_names = {
    2048: "talenom",
    1102: "cramo",
    1091: "sanoma",
    1196: "afarak group"
}
company_names = {}


class Test(unittest.TestCase):

    def test_scrape_companies_sequentially(self):
        time0 = time.time()
        scrapeKL.scrape_companies_sequentially(storage_directory, company_names)

        print("\nSEQUENTIALLY\ttime: {:.2f} s".format(time.time() - time0))

        """
        self.assertTrue(os.path.isfile(filename))
        output_str = scrapeKL.print_companies(filename, return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrapeKL.print_company_metrics(filename, "metrics", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrapeKL.print_company_metrics(filename, "metrics_simple", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrapeKL.print_company_metrics(filename, "calculations", return_output=True)
        self.assertGreater(len(output_str), 0)
        os.remove(filename)
        """

    def test_scrape_companies_with_threads(self):
        company_list = []
        company_failed_count = 0
        filename_metrics = ""

        time0 = time.time()
        scrapeKL.scrape_companies_with_threads(storage_directory, filename_metrics,
                                               company_names, company_list, company_failed_count)

        print("\nTHREADS\t\ttime: {:.2f} s".format(time.time() - time0))

        self.assertIsInstance(filename_metrics, str)
        self.assertEqual(len(company_list), 3)
        for company in company_list:
            self.assertIsInstance(company, scraping.Company)
            self.assertIsInstance(company.json_metrics, str)
            self.assertGreater(len(company.json_metrics), 1000)

    def test_scrape_companies_with_processes(self):
        json_metrics_list = []

        time0 = time.time()
        scrapeKL.scrape_companies_with_processes(storage_directory, company_names, json_metrics_list)

        print("\nPROCESSES\ttime: {:.2f} s".format(time.time() - time0))

        #self.assertEqual(len(company_list), 3)
        self.assertGreater(len(json_metrics_list), 0)
        #print("json_metrics_list:")
        for json_metrics in json_metrics_list:
            self.assertIsInstance(json_metrics, str)
            self.assertGreater(len(json_metrics), 35)
            """
            if len(json_metrics) < 81:
                print(json_metrics)
            else:
                print(json_metrics[1:80] + "...")
            """


if __name__ == '__main__':
    unittest.main()
