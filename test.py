"""
python -m unittest -v
"""
import unittest, logging
from datetime import datetime, date

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

    def test_pretty_val(self):
        """ expected_type can be:
                int, float, str, date
            types not implemented:
                datetime, boolean
        """
        test_pretty_val_Equal(self, int, 12, 12)
        test_pretty_val_Equal(self, int, "12", 12)
        test_pretty_val_Equal(self, int, "100milj.eur", 1e8)
        test_pretty_val_Equal(self, int, "3.4milj.eur", 34e5)
        for v in ["38.2", " ", "", None, "he", "3,5", 2.1, "2miljard.eur"]:
            self.assertRaises(scraping.ScrapeException, scraping.pretty_val, v, int)

        test_pretty_val_Equal(self, float, 38.23, 38.23)
        test_pretty_val_Equal(self, float, "38.23", 38.23)
        test_pretty_val_Equal(self, float, "3.4milj.eur", 34e5)
        test_pretty_val_Equal(self, float, 2.1, 2.1)
        for v in [" ", "", None, "he", "3,5"]:
            self.assertRaises(scraping.ScrapeException, scraping.pretty_val, v, float)

        test_pretty_val_Equal(self, str, "38.23", "38.23")
        test_pretty_val_Equal(self, str, "fooBar\n", "foobar")
        test_pretty_val_Equal(self, str, " aåäöox ", "aaaoox")
        test_pretty_val_Equal(self, str, None, "")
        test_pretty_val_Equal(self, str, "", "")
        test_pretty_val_Equal(self, str, " ", "")
        for v in ["\x9a"]:
            self.assertRaises(scraping.ScrapeException, scraping.pretty_val, v, str)

        # DD.MM.YYYY
        test_pretty_val_Equal(self, date, date(2016, 2, 1), date(2016, 2, 1))
        test_pretty_val_Equal(self, date, "12.11.2002", date(2002, 11, 12))
        test_pretty_val_Equal(self, date, "01.02.2016", date(2016, 2, 1))
        for v in ["01.20.2015", "01-02-2016", "01022016", "1.1.1aaaaa", "", None, " "]:
            self.assertRaises(scraping.ScrapeException, scraping.pretty_val, v, date)

        self.assertRaises(scraping.ScrapeException, scraping.pretty_val, "value", datetime)
        self.assertRaises(scraping.ScrapeException, scraping.pretty_val, "value", "type")

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
        one_expected_osinko_2051 = {'oikaistu_euroina': 0.5,
                                    'maara': 0.5,
                                    'tuotto_%': 3.7,
                                    'irtoaminen': date(2017, 5, 18),
                                    'valuutta': 'eur',
                                    'vuosi': 2017,
                                    'lisatieto': 'paaomanpalautus'
        }
        one_expected_osinko_1050 = {'lisatieto': '',
                                    'oikaistu_euroina': 0.37,
                                    'maara': 0.37,
                                    'tuotto_%': 2.1,
                                    'irtoaminen': date(2006, 3, 31),
                                    'vuosi': 2006,
                                    'valuutta': 'eur'
        }
        one_expected_osinko_1083 = {'valuutta': 'eur',
                                    'irtoaminen': date(2003, 4, 25),
                                    'oikaistu_euroina': 0.18,
                                    'lisatieto': '',
                                    'maara': 0.23,
                                    'tuotto_%': 4.8,
                                    'vuosi': 2003
        }
        test_get_osinko_Controll(self, 2051, one_expected_osinko_2051)
        test_get_osinko_Controll(self, 1050, one_expected_osinko_1050)
        test_get_osinko_Controll(self, 1083, one_expected_osinko_1083)

def test_pretty_val_Equal(tester, expected_type, v, expected_v):
    pretty_v = scraping.pretty_val(v, expected_type)
    tester.assertEqual(pretty_v, expected_v)
    tester.assertIsInstance(pretty_v, expected_type)

def test_get_osinko_Controll(tester, company_id, one_expected_osinko):
    type_dict = {"vuosi": int,
                 "irtoaminen": date,
                 "oikaistu_euroina": float,
                 "maara": float,
                 "valuutta": str,
                 "tuotto_%": float,
                 "lisatieto": str
    }

    url = osingot_yritys_url.format(company_id)
    osingot = scraping.get_osingot_NEW(url)
    matches = 0
    for top_key in osingot:
        if osingot[top_key]["irtoaminen"] == one_expected_osinko["irtoaminen"] and \
           osingot[top_key]["maara"] == one_expected_osinko["maara"]:
            tester.assertDictEqual(osingot[top_key], one_expected_osinko)
            matches += 1
        for key in osingot[top_key]:
            tester.assertIsInstance(osingot[top_key][key], type_dict[key])
    tester.assertEqual(matches, 1)


class Test_scrape_KL(unittest.TestCase):

    def test_scrape_KL_placeholder(self):
        self.assertEqual(3,3)


if __name__ == '__main__':
    unittest.main()
