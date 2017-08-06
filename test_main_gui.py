import os, unittest, logging

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

    def test_scrapeThread(self):
        pass


if __name__ == '__main__':
    unittest.main()
