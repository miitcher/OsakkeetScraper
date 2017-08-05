import os, unittest, logging

fast_tests = True
show_debug = False

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if not show_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

import scrape_KL


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"

storage_directory = "scrapes"

some_company_ids = [2048, 1032, 1135, 1120, 1105]


class Test(unittest.TestCase):
    @unittest.skipIf(fast_tests, "fast testing")
    def test_scrape_companies_All(self):
        #scrape_KL.scrape_companies(storage_directory)
        # TODO: Not ready
        pass

    def test_scrape_companies_One(self):
        filename = scrape_KL.scrape_companies(storage_directory, {2048:"talenom"})
        self.assertTrue(os.path.isfile(filename))

        output_str = scrape_KL.print_companies(filename, return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrape_KL.print_company_metrics(filename, "metrics", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrape_KL.print_company_metrics(filename, "metrics_simple", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrape_KL.print_company_metrics(filename, "calculations", return_output=True)
        self.assertGreater(len(output_str), 0)
        # TODO: Better validation of print output.

        os.remove(filename)

    # Maby these test should just be done in test_storage.py.
    """ # TODO: When all scraping.get_* functions fixed
        #    --> update: "test\\scrape_metrics_one_comp.tsv"
    @unittest.skipIf(skip_print_tests, "clear")
    def test_print_companies(self):
        filename = "test\\scrape_metrics_one_comp.tsv"
        scrape_KL.print_companies(filename)

    @unittest.skipIf(skip_print_tests, "clear")
    def test_print_company_metrics(self):
        filename = "test\\scrape_metrics_one_comp.tsv"
        scrape_KL.print_company_metrics(filename, "metrics")
        scrape_KL.print_company_metrics(filename, "metrics_simple")
        scrape_KL.print_company_metrics(filename, "calculations")
    """

    def test_filter_companies(self):
        pass

    def test_organize_companies(self):
        pass


if __name__ == '__main__':
    unittest.main()
