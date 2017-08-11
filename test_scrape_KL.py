import os, unittest, logging

import scrape_KL


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

some_company_ids = [2048, 1032, 1135, 1120, 1105]


class Test(unittest.TestCase):

    def test_scrape_and_store_companies(self):
        # Create and start three scrapeCompanyThreads and save companies
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma"
        }

    """
    def test_scrape_companies_One_OLD(self):
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
    """


if __name__ == '__main__':
    unittest.main()
