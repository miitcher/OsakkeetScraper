"""
python -m unittest -v
"""
import unittest, logging

import scraping
#import scrape_KL

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
logger.setLevel(logging.DEBUG)

url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"


class Test_scraping(unittest.TestCase):

    def test_fix_str(self):
        pass

    def test_fix_str_noncompatible_chars_in_unicode(self):
        pass

    def test_scrape_company_names(self):
        company_names = scraping.scrape_company_names()
        for key in company_names:
            self.assertTrue(type(key) == int)
            self.assertTrue(type(company_names[key]) == str)
        self.assertEqual(company_names[2048], "talenom")
        self.assertEqual(company_names[1032], "fortum")
        self.assertEqual(company_names[1135], "upm-kymmene")
        self.assertEqual(company_names[1120], "huhtamaki")
        self.assertEqual(company_names[1105], "alandsbanken b")

    def test_get_osingot(self):
        # TODO: Not ready yet...
        #url = osingot_yritys_url.format(1050) # has not lisatieto metrics
        url = osingot_yritys_url.format(2051) # has lisatieto metrics
        osingot = scraping.get_osingot_NEW(url)
        
        pretty_osingot = scraping.Company.list_to_pretty_dict(scraping.get_osingot(url))
        
        print()
        #print(osingot)
        for i in osingot:
            print(osingot[i])
        print("len: " + str(len(osingot)))
        
        print()
        #print(pretty_osingot)
        for i in pretty_osingot:
            print(pretty_osingot[i])
        print("len: " + str(len(pretty_osingot)))
        


class Test_scrape_KL(unittest.TestCase):

    def test_scrape_KL_placeholder(self):
        self.assertEqual(3,3)


if __name__ == '__main__':
    unittest.main()
