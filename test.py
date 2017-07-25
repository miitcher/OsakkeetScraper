"""
python -m unittest -v
"""
import os, unittest, logging
from datetime import datetime, date

import scraping
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


class Test_scraping(unittest.TestCase):
    @unittest.skipIf(skip_bigger_scrapes, "fast testing")
    def test_Company_scrape(self):
        #company = scraping.Company(c_id=1930, c_name="orion a")
        company = scraping.Company(c_id=2048, c_name="talenom")
        company.scrape()

    def test_pretty_val(self):
        # expected_type can be: int, float, str, date
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

        # DD.MM.YYYY --> YYYY-MM-DD
        test_pretty_val_Equal(self, date, "2016-02-01", "2016-02-01")
        test_pretty_val_Equal(self, date, "12.11.2002", "2002-11-12")
        test_pretty_val_Equal(self, date, "01.02.2016", "2016-02-01")
        for v in ["01.20.2015", "01-02-2016", "01022016",
                  "1.1.1aaaaa", "i01.02.2011i", "", None, " "]:
            self.assertRaises(scraping.ScrapeException, scraping.pretty_val, v, date)

        self.assertRaises(scraping.ScrapeException, scraping.pretty_val, "value", datetime)
        self.assertRaises(scraping.ScrapeException, scraping.pretty_val, "value", "type")
    '''
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

    def test_get_kurssi(self):
        for company_id in some_company_ids:
            url = kurssi_url.format(company_id)
            kurssi = scraping.get_kurssi(url)
            self.assertIsInstance(kurssi, float)

    def test_get_kuvaus(self):
        for company_id in some_company_ids:
            url = kurssi_url.format(company_id)
            kuvaus = scraping.get_kuvaus(url)
            self.assertIsInstance(kuvaus, str)

    def test_get_osingot(self):
        one_expected_osinko_2051 = {
            'oikaistu_euroina': 0.5,
            'maara': 0.5,
            'tuotto_%': 3.7,
            'irtoaminen': "2017-05-18",
            'valuutta': 'eur',
            'vuosi': 2017,
            'lisatieto': 'paaomanpalautus'
        }
        one_expected_osinko_1050 = {
            'lisatieto': '',
            'oikaistu_euroina': 0.37,
            'maara': 0.37,
            'tuotto_%': 2.1,
            'irtoaminen': "2006-03-31",
            'vuosi': 2006,
            'valuutta': 'eur'
        }
        one_expected_osinko_1083 = {
            'valuutta': 'eur',
            'irtoaminen': "2003-04-25",
            'oikaistu_euroina': 0.18,
            'lisatieto': '',
            'maara': 0.23,
            'tuotto_%': 4.8,
            'vuosi': 2003
        }
        test_get_osinko_Controll(self, 2051, one_expected_osinko_2051)
        test_get_osinko_Controll(self, 1050, one_expected_osinko_1050)
        test_get_osinko_Controll(self, 1083, one_expected_osinko_1083)
    '''
    def test_get_perustiedot(self):
        part_of_expected_perustiedot_2048 = {
            'toimiala': 'teollisuustuotteet ja -palvelut',
            'kaupankaynti_valuutta': 'eur',
            'listattu': '2015-06-11',
            'kaupankayntitunnus': 'tnom',
            'toimialaluokka': 'teollisuushyodykkeet ja -palvelut',
            'isin-koodi': 'fi4000153580',
            'nimellisarvo': '',
            'porssi': 'omx helsinki'
        }
        part_of_expected_perustiedot_1032 = {
            'porssi': 'omx helsinki',
            'isin-koodi': 'fi0009007132',
            'toimiala': 'yleishyodylliset palvelut',
            'kaupankaynti_valuutta': 'eur',
            'kaupankayntitunnus': 'fortum',
            'nimellisarvo': '',
            'listattu': '1998-12-18',
            'toimialaluokka': 'yleishyodyllliset palvelut'
        }
        part_of_expected_perustiedot_1135 = {
            'toimialaluokka': 'perusluonnonvarat',
            'porssi': 'omx helsinki',
            'kaupankaynti_valuutta': 'eur',
            'kaupankayntitunnus': 'upm',
            'toimiala': 'perusteollisuus',
            'nimellisarvo': '',
            'listattu': '1996-05-02',
            'isin-koodi': 'fi0009005987',
        }
        test_get_perustiedot_Controll(self, 2048, part_of_expected_perustiedot_2048)
        test_get_perustiedot_Controll(self, 1032, part_of_expected_perustiedot_1032)
        test_get_perustiedot_Controll(self, 1135, part_of_expected_perustiedot_1135)

def test_pretty_val_Equal(tester, expected_type, v, expected_v):
    pretty_v = scraping.pretty_val(v, expected_type)
    tester.assertEqual(pretty_v, expected_v)
    if expected_type == date:
        tester.assertIsInstance(pretty_v, str)
    else:
        tester.assertIsInstance(pretty_v, expected_type)

def test_get_osinko_Controll(tester, company_id, one_expected_osinko):
    type_dict = {
        "vuosi": int,
        "irtoaminen": str,
        "oikaistu_euroina": float,
        "maara": float,
        "valuutta": str,
        "tuotto_%": float,
        "lisatieto": str
    }

    url = osingot_yritys_url.format(company_id)
    osingot = scraping.get_osingot(url)
    matches = 0
    for top_key in osingot:
        tester.assertIsInstance(top_key, str)
        tester.assertEqual(len(osingot[top_key]), 7)
        if osingot[top_key]["irtoaminen"] == one_expected_osinko["irtoaminen"] and \
           osingot[top_key]["maara"] == one_expected_osinko["maara"]:
            tester.assertDictEqual(osingot[top_key], one_expected_osinko)
            matches += 1
        for key in osingot[top_key]:
            tester.assertIsInstance(osingot[top_key][key], type_dict[key])
    tester.assertEqual(matches, 1)

def test_get_perustiedot_Controll(tester, company_id, part_of_expected_perustiedot):
    type_dict = {
        "porssi": str,
        "listattu": str,
        "kaupankayntitunnus": str,
        "isin-koodi": str,
        "toimialaluokka": str,
        "nimellisarvo": str,
        "kaupankaynti_valuutta": str,
        "toimiala": str,
        "markkina-arvo": float,
        "osakkeet_kpl": int
    }
    """
    url_ku = kurssi_url.format(company_id)
    per_old = scraping.Company.dict_to_pretty_dict(scraping.get_perustiedot_OLD(url_ku))

    print()
    print("----")
    for i in per_old:
        print(i + "\t" + str(per_old[i]))
    print("++++")
    """
    url = kurssi_url.format(company_id)
    perustiedot = scraping.get_perustiedot(url)
    tester.assertEqual(len(perustiedot), 10)
    for key in perustiedot:
        #print(key + "\t" + str(perustiedot[key]))
        tester.assertIsInstance(perustiedot[key], type_dict[key])
        if type_dict[key] == str:
            tester.assertEqual(perustiedot[key], part_of_expected_perustiedot[key])


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
        #    --> update: "testfiles\\scrape_metrics_one_comp.tsv"
    @unittest.skipIf(skip_print_tests, "clear")
    def test_print_companies(self):
        filename = "testfiles\\scrape_metrics_one_comp.tsv"
        scrape_KL.print_companies(filename)

    @unittest.skipIf(skip_print_tests, "clear")
    def test_print_company_metrics(self):
        filename = "testfiles\\scrape_metrics_one_comp.tsv"
        scrape_KL.print_company_metrics(filename, "metrics")
        scrape_KL.print_company_metrics(filename, "metrics_simple")
        scrape_KL.print_company_metrics(filename, "calculations")
    """

if __name__ == '__main__':
    unittest.main()
