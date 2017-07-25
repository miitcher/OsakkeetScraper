import os, unittest, logging

import scrape_KL


skip_bigger_scrapes = False
skip_print_tests = False
"""
skip_bigger_scrapes = True
skip_print_tests = True
"""

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if skip_print_tests:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"

storage_directory = "scrapes"

some_company_ids = [2048, 1032, 1135, 1120, 1105]


class Test_scrape_KL(unittest.TestCase):
    @unittest.skipIf(skip_bigger_scrapes or skip_print_tests, "fast testing & clear")
    def test_scrape_companies_AND_other(self):
        # scraping takes so long; so we do it just once

        # all companies:
        #scrape_KL.scrape_companies(storage_directory)

        # one company:
        filename = scrape_KL.scrape_companies(storage_directory, {2048:"talenom"})
        self.assertTrue(os.path.isfile(filename))

        scrape_KL.print_companies(filename)
        scrape_KL.print_company_metrics(filename, "metrics")
        scrape_KL.print_company_metrics(filename, "metrics_simple")
        scrape_KL.print_company_metrics(filename, "calculations")

        os.remove(filename)

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


if __name__ == '__main__':
    unittest.main()
