import unittest, logging, os, time

import scrapeKL


SHOW_DEBUG = False

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

    def test_scrape_companies(self):
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma",
            1196: "afarak group"
        }
        #company_names = {} # For scraping every company
        showProgress = False

        time0 = time.time()
        json_metrics_list, failed_company_dict, metricsfilename = scrapeKL.scrape_companies(
            storage_directory, company_names, showProgress
        )
        logger.debug("\nScraping time: {:.2f} s".format(time.time() - time0))

        self.assertIsInstance(metricsfilename, str)
        for json_metrics in json_metrics_list:
            self.assertIsInstance(json_metrics, str)
            self.assertGreater(len(json_metrics), 35)
            if len(json_metrics) < 100:
                logger.debug("Failed: " + json_metrics[1:])
            else:
                logger.debug(json_metrics[1:80] + "...")
        for company_id in failed_company_dict:
            logger.debug("Failed list: ({}, {})".format(company_id, failed_company_dict[company_id]))

        self.assertEqual(len(failed_company_dict), 1)
        self.assertEqual(len(json_metrics_list), 4)

        os.remove(metricsfilename)


if __name__ == '__main__':
    unittest.main()
