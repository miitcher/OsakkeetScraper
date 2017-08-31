import unittest
from datetime import datetime, date
from multiprocessing import Queue
import scrape_logger

from scraping import Scraper
import scraping


level = "WARNING"
#level = "INFO"
#level = "DEBUG"
logger = scrape_logger.setup_logger(level)


some_company_ids = [2048, 1032, 1135, 1120, 1105]


class Test(unittest.TestCase):

    def test_scrape_company_target_function(self):
        metrics_queue = Queue() # Company.metrics dicts are stored here
        scraping.scrape_company_target_function(
            metrics_queue, 2048, "talenom"
        )
        metrics = metrics_queue.get() # waits on the next value
        logger.debug("company_name: {}".format(metrics['company_name']))

        self.assertIsInstance(metrics, dict)
        self.assertGreater(len(metrics), 5)

    def test_scrape_companies_with_processes(self):
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma",
            1196: "afarak group"
        }
        showProgress = False

        metrics_list = scraping.scrape_companies_with_processes(
            company_names, showProgress
        )

        for metrics in metrics_list:
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 1)
            logger.debug("company_name: {}".format(metrics['company_name']))

    def test_Scraper_scrape(self):
        scraper = scraping.Scraper(2048)
        metrics = scraper.scrape()
        self.assertIsInstance(metrics, dict)
        self.assertEqual(len(metrics), 16)

    def test_pretty_val(self):
        # expected_type can be: int, float, str, date

        # OUTPUT IS NONE
        for v in ["-", "", " \t", None]:
            test_pretty_val_Equal(self, int, v, None)
            test_pretty_val_Equal(self, float, v, None)
            test_pretty_val_Equal(self, str, v, None)
            test_pretty_val_Equal(self, date, v, None)

        # INT
        test_pretty_val_Equal(self, int, 12, 12)
        test_pretty_val_Equal(self, int, "12", 12)
        test_pretty_val_Equal(self, int, "100milj.eur", 1e8)
        test_pretty_val_Equal(self, int, "3.4milj.eur", 34e5)
        for v in ["38.2", "he", "3,5", 2.1, "2miljard.eur"]:
            self.assertRaises(scraping.ScrapeException,
                              Scraper.pretty_val_st, v, int)

        # FLOAT
        test_pretty_val_Equal(self, float, 38.23, 38.23)
        test_pretty_val_Equal(self, float, "38.23", 38.23)
        test_pretty_val_Equal(self, float, "3.4milj.eur", 34e5)
        test_pretty_val_Equal(self, float, 2.1, 2.1)
        for v in ["he"]:
            self.assertRaises(scraping.ScrapeException,
                              Scraper.pretty_val_st, v, float)

        # STR
        test_pretty_val_Equal(self, str, "38.23", "38.23")
        test_pretty_val_Equal(self, str, "fooBar\n", "foobar")
        test_pretty_val_Equal(self, str, " aåäöox ", "aaaoox")

        # DATE
        # DD.MM.YYYY --> YYYY-MM-DD
        test_pretty_val_Equal(self, date, "2016-02-01", "2016-02-01")
        test_pretty_val_Equal(self, date, "12.11.2002", "2002-11-12")
        test_pretty_val_Equal(self, date, "01.02.2016", "2016-02-01")
        for v in ["01.20.2015", "01-02-2016", "01022016",
                  "1.1.1aaaaa", "i01.02.2011i"]:
            self.assertRaises(scraping.ScrapeException,
                              Scraper.pretty_val_st, v, date)

        # OTHER TYPES
        self.assertRaises(scraping.ScrapeException,
                          Scraper.pretty_val_st, "value", datetime)
        self.assertRaises(scraping.ScrapeException,
                          Scraper.pretty_val_st, "value", "type")

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

    def test_get_name(self):
        for company_id in some_company_ids:
            scraper = Scraper(company_id)
            name = scraper.get_name()
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 2)

    def test_get_kurssi(self):
        for company_id in some_company_ids:
            scraper = Scraper(company_id)
            kurssi = scraper.get_kurssi()
            self.assertIsInstance(kurssi, float)

    def test_get_kuvaus(self):
        for company_id in some_company_ids:
            scraper = Scraper(company_id)
            kuvaus = scraper.get_kuvaus()
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
            'lisatieto': None,
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
            'lisatieto': None,
            'maara': 0.23,
            'tuotto_%': 4.8,
            'vuosi': 2003
        }
        test_get_osinko_Controll(self, 2051, one_expected_osinko_2051)
        test_get_osinko_Controll(self, 1050, one_expected_osinko_1050)
        test_get_osinko_Controll(self, 1083, one_expected_osinko_1083)

    def test_get_perustiedot(self):
        part_of_expected_perustiedot_2048 = {
            'toimiala': 'teollisuustuotteet ja -palvelut',
            'kaupankaynti_valuutta': 'eur',
            'listattu': '2015-06-11',
            'kaupankayntitunnus': 'tnom',
            'toimialaluokka': 'teollisuushyodykkeet ja -palvelut',
            'isin-koodi': 'fi4000153580',
            'nimellisarvo': None,
            'porssi': 'omx helsinki'
        }
        part_of_expected_perustiedot_1032 = {
            'porssi': 'omx helsinki',
            'isin-koodi': 'fi0009007132',
            'toimiala': 'yleishyodylliset palvelut',
            'kaupankaynti_valuutta': 'eur',
            'kaupankayntitunnus': 'fortum',
            'nimellisarvo': None,
            'listattu': '1998-12-18',
            'toimialaluokka': 'yleishyodyllliset palvelut'
        }
        part_of_expected_perustiedot_1135 = {
            'toimialaluokka': 'perusluonnonvarat',
            'porssi': 'omx helsinki',
            'kaupankaynti_valuutta': 'eur',
            'kaupankayntitunnus': 'upm',
            'toimiala': 'perusteollisuus',
            'nimellisarvo': None,
            'listattu': '1996-05-02',
            'isin-koodi': 'fi0009005987',
        }
        test_get_perustiedot_Controll(self, 2048,
                                      part_of_expected_perustiedot_2048)
        test_get_perustiedot_Controll(self, 1032,
                                      part_of_expected_perustiedot_1032)
        test_get_perustiedot_Controll(self, 1135,
                                      part_of_expected_perustiedot_1135)

    def test_get_tunnuslukuja(self):
        for company_id in some_company_ids:
            test_get_tunnuslukuja_Controll(self, company_id)

    def test_get_toiminnan_laajuus(self):
        for company_id in some_company_ids:
            test_get_toiminnan_laajuus_Controll(self, company_id)

    def test_get_kannattavuus(self):
        for company_id in some_company_ids:
            test_get_kannattavuus_Controll(self, company_id)

    def test_get_vakavaraisuus(self):
        for company_id in some_company_ids:
            test_get_vakavaraisuus_Controll(self, company_id)

    def test_get_maksuvalmius(self):
        for company_id in some_company_ids:
            test_get_maksuvalmius_Controll(self, company_id)

    def test_get_sijoittajan_tunnuslukuja(self):
        for company_id in some_company_ids:
            test_get_sijoittajan_tunnuslukuja_Controll(self, company_id)


def test_pretty_val_Equal(tester, expected_type, v, expected_v):
    pretty_v = Scraper.pretty_val_st(v, expected_type)
    tester.assertEqual(pretty_v, expected_v)
    if pretty_v is None:
        pass
    elif expected_type == date:
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
    scraper = Scraper(company_id)
    osingot = scraper.get_osingot()
    matches = 0
    for top_key in osingot:
        tester.assertIsInstance(top_key, str)
        tester.assertEqual(len(osingot[top_key]), 7)
        if osingot[top_key]["irtoaminen"] == one_expected_osinko["irtoaminen"] \
        and osingot[top_key]["maara"] == one_expected_osinko["maara"]:
            tester.assertDictEqual(osingot[top_key], one_expected_osinko)
            matches += 1
        for key in osingot[top_key]:
            if osingot[top_key][key] is not None:
                tester.assertIsInstance(osingot[top_key][key], type_dict[key])
    tester.assertEqual(matches, 1)

def test_get_perustiedot_Controll(tester, company_id,
                                  part_of_expected_perustiedot):
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
    scraper = Scraper(company_id)
    perustiedot = scraper.get_perustiedot()
    tester.assertEqual(len(perustiedot), 10)
    for key in perustiedot:
        if perustiedot[key] is not None:
            tester.assertIsInstance(perustiedot[key], type_dict[key])
        if type_dict[key] == str:
            tester.assertEqual(perustiedot[key],
                               part_of_expected_perustiedot[key])

def test_get_tunnuslukuja_Controll(tester, company_id):
    scraper = Scraper(company_id)
    tunnuslukuja = scraper.get_tunnuslukuja()
    tester.assertEqual(len(tunnuslukuja), 6)
    for key in tunnuslukuja:
        tester.assertIsInstance(tunnuslukuja[key], float)

def assert_tulostietoja(tester, company_id, tulostieto, head_count):
    if tulostieto:
        tester.assertLess(len(tulostieto), 6)
        tester.assertGreater(len(tulostieto), 3)
        for key in tulostieto:
            tester.assertEqual(len(tulostieto[key]), head_count)
            for sub_key in tulostieto[key]:
                v = tulostieto[key][sub_key]
                if v is not None:
                    tester.assertIsInstance(v, float)
    else:
        tester.assertEqual(company_id, 1105)

def test_get_toiminnan_laajuus_Controll(tester, company_id):
    scraper = Scraper(company_id)
    toiminnan_laajuus = scraper.get_toiminnan_laajuus()
    assert_tulostietoja(tester, company_id, toiminnan_laajuus, 7)

def test_get_kannattavuus_Controll(tester, company_id):
    scraper = Scraper(company_id)
    kannattavuus = scraper.get_kannattavuus()
    assert_tulostietoja(tester, company_id, kannattavuus, 7)

def test_get_vakavaraisuus_Controll(tester, company_id):
    scraper = Scraper(company_id)
    vakavaraisuus = scraper.get_vakavaraisuus()
    assert_tulostietoja(tester, company_id, vakavaraisuus, 6)

def test_get_maksuvalmius_Controll(tester, company_id):
    scraper = Scraper(company_id)
    maksuvalmius = scraper.get_maksuvalmius()
    assert_tulostietoja(tester, company_id, maksuvalmius, 3)

def test_get_sijoittajan_tunnuslukuja_Controll(tester, company_id):
    scraper = Scraper(company_id)
    sijoittajan_tunnuslukuja = scraper.get_sijoittajan_tunnuslukuja()
    assert_tulostietoja(tester, company_id, sijoittajan_tunnuslukuja, 12)


if __name__ == '__main__':
    unittest.main()
