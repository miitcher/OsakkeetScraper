import requests, re, logging, traceback
from bs4 import BeautifulSoup
from datetime import date
from multiprocessing import Process, Queue
import scrape_logger

#logger = logging.getLogger('root')

#level = "WARNING"
#level = "INFO"
level = "DEBUG"
logger = scrape_logger.setup_logger(level, "scraping")
scrape_logger.set_logger_level(logger, level)


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + \
    "porssikurssit/osake/tulostiedot.jsp?klid={}"

date_format = "%Y-%m-%d" # YYYY-MM-DD
date_short_format = "%y-%m-%d" # YY-MM-DD
datetime_format = "%y-%m-%d_%H-%M-%S" # YY-MM-DD_HH-MM-SS: for filename
date_pattern_0 = re.compile("^\d{4}\-\d{2}\-\d{2}$") # YYYY-MM-DD
date_pattern_1 = re.compile("^\d{2}\.\d{2}\.\d{4}$") # DD.MM.YYYY


class ScrapeException(Exception):
    pass


def scrape_company_target_function(queue, company_id, company_name):
    # Used as target function for multitreading.Process
    scraper = Scraper(company_id)
    metrics = scraper.scrape()
    metrics["company_id"] = company_id
    metrics["company_name"] = company_name
    queue.put(metrics)

def scrape_companies_with_processes(company_names, showProgress=True):
    metrics_queue = Queue() # metrics dictionaries are stored here
    # TODO: Would Pool be better?
    for company_id in company_names:
        process = Process(
            target=scrape_company_target_function,
            args=(metrics_queue, company_id, company_names[company_id]),
            name="({}, {})".format(company_id, company_names[company_id])
        )
        logger.debug("Starting {}".format(process))
        process.start()

    metrics_list = []
    len_all = len(company_names)
    len_metrics_list = 0 # counter
    while True:
        if len_metrics_list == len_all:
            break
        # .get() waits on the next value.
        # Then .join() is not needed for processes.
        metrics_list.append(metrics_queue.get())
        len_metrics_list += 1
        if showProgress:
            if len_metrics_list%5 == 0:
                logger.info("\t{:3}/{} - {:2}%".format(
                    len_metrics_list, len_all,
                    round( 100 * len_metrics_list / len_all )
                ))

    return metrics_list

def scrape_company_names():
    soup = Scraper.get_raw_soup(osingot_url)
    form_tags = soup.find_all('form')
    option_tags = form_tags[2].find_all('option')
    company_names = {}
    for i in option_tags:
        company_id = i.attrs['value']
        company_name = i.string
        if company_id and company_name:
            company_id = int(company_id)
            company_name = Scraper.pretty_val_st(company_name, str)
            company_names[company_id] = company_name
        elif company_name != "Valitse osake":
            raise ScrapeException(
                "Unexpected: id:[{}], name:[{}]".format(
                    company_id, company_name
                )
            )
    return company_names


class Company():
    def __init__(self, c_metrics):
        assert isinstance(c_metrics, dict) and len(c_metrics) > 1
        self.metrics = c_metrics
        self.company_id = self.metrics["company_id"]
        self.company_name = self.metrics["company_name"]

        assert self.company_id
        assert isinstance(self.company_id, int)
        assert isinstance(self.company_name, str)

        self.calculations = {}

    def __repr__(self):
        return "Company({}, {})".format(self.company_id, self.company_name)

    def calculate(self):
        assert len(self.metrics) > 2, \
            "Too few metrics. len(self.metrics)={}".fomat(len(self.metrics))
        self.calculate_osinko()
        self.collect_metrics()
        self.calculate_fresh()

    def addCalc(self, key, value):
        assert not str(key) in self.calculations
        self.calculations[str(key)] = value

    def calculate_osinko(self):
        # steady osinko: osinkotuotto > 0% for five years
        current_year = int(date.today().strftime("%Y")) # YYYY
        osinko_tuotto_prosentti = {}
        osinko_euro = {}
        for year in range(current_year-4, current_year+1):
            osinko_tuotto_prosentti[str(year)] = 0
            osinko_euro[str(year)] = 0

        for top_key in self.metrics["osingot"]:
            osinko_dict = self.metrics["osingot"][top_key]
            osinko_year = str(osinko_dict["vuosi"])
            if osinko_year in osinko_tuotto_prosentti:
                osinko_tuotto_prosentti[osinko_year] += osinko_dict["tuotto_%"]
                osinko_euro[osinko_year] += osinko_dict["oikaistu_euroina"]

        steady_osinko_bool = 1 # 1: True, 0: False
        for year in osinko_tuotto_prosentti:
            if osinko_tuotto_prosentti[year] <= 0:
                steady_osinko_bool = 0
                break

        self.addCalc("osinko_tuotto_%", osinko_tuotto_prosentti)
        self.addCalc("osinko_euro", osinko_euro)
        self.addCalc("steady_osinko_bool", steady_osinko_bool)

    def set_tt_current_key(self):
        # "12/16", used for dictionaries scraped from the tulostiedot-page
        self.tt_current_key = None
        current_year = int(date.today().strftime("%y")) # YY
        key_dict = {} # keys_dict(year_int) = key_str
        for key in self.metrics["kannattavuus"]:
            if key.endswith("/{}".format(current_year)) or \
               key.endswith("/{}".format(current_year - 1)):
                parts = key.split("/")
                key_dict[int(parts[1])] = key
        if current_year in key_dict:
            self.tt_current_key = key_dict[current_year]
        elif (current_year - 1) in key_dict:
            self.tt_current_key = key_dict[(current_year - 1)]
        else:
            all_keys = []
            for key in self.metrics["kannattavuus"]:
                all_keys.append(key)
            raise ScrapeException("Unexpected keys: {}".format(str(all_keys)))
        assert self.tt_current_key
        assert self.tt_current_key == "12/16" # Changes when time passes

    def collect_metrics(self):
        # TODO: Could this be written some other way?
        # Sidenote: not using: toiminnan laajuus, maksuvalmius

        self.addCalc("company_id", self.metrics["company_id"])
        self.addCalc("company_name", self.metrics["company_name"])
        self.addCalc("kurssi", self.metrics["kurssi"])
        self.addCalc("kuvaus", self.metrics["kuvaus"])
        self.addCalc("scrape_date", self.metrics["scrape_date"])

        self.addCalc("toimiala", self.metrics["perustiedot"]["toimiala"])
        self.addCalc("toimialaluokka", self.metrics["perustiedot"]["toimialaluokka"])
        self.addCalc("osakkeet_kpl", self.metrics["perustiedot"]["osakkeet_kpl"])

        try:
            self.set_tt_current_key() # taloustiedot_current_key: "12/16"
        except ScrapeException:
            logger.debug("Missing metrics")
            self.tt_current_key = None
        self.addCalc("tt_current_key", self.tt_current_key)

        if self.tt_current_key:
            self.addCalc("ROE", self.metrics["kannattavuus"][self.tt_current_key]["oman paaoman tuotto, %"])
            self.addCalc("nettotulos", self.metrics["kannattavuus"][self.tt_current_key]["nettotulos"])

            self.addCalc("omavaraisuusaste", self.metrics["vakavaraisuus"][self.tt_current_key]["omavaraisuusaste, %"])
            self.addCalc("gearing", self.metrics["vakavaraisuus"][self.tt_current_key]["nettovelkaantumisaste, %"])

            self.addCalc("PB", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["p/b-luku"])
            self.addCalc("PE", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["p/e-luku"])
            self.addCalc("E", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["tulos (e)"])
            self.addCalc("P", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["markkina-arvo (p)"])

    def calculate_fresh(self):
        calc = self.calculations
        current_year = date.today().strftime("%Y") # "YYYY"
        # the metrics below are fresher, because they are calculated with the current stock price
        self.addCalc("calc_osinkotuotto_percent", round( 100 * calc["osinko_euro"][current_year] / calc["kurssi"], 2))
        self.addCalc("calc_P", round( calc["osakkeet_kpl"] * calc["kurssi"] / 1e6, 4))

        if self.tt_current_key:
            self.addCalc("calc_P_factor", round( calc["calc_P"] / calc["P"], 4))
            self.addCalc("calc_PB", round( calc["calc_P_factor"] * calc["PB"], 2))
            self.addCalc("calc_PE", round( calc["calc_P_factor"] * calc["PE"], 2))


class Scraper():
    def __init__(self, company_id):
        assert isinstance(company_id, int)
        self.metrics = {}
        self.company_id = company_id
        self.url_osingot = osingot_yritys_url.format(company_id)
        self.url_kurssi = kurssi_url.format(company_id)
        self.url_tulostiedot = kurssi_tulostiedot_url.format(company_id)

        self.soup_osingot = None
        self.soup_kurssi = None
        self.soup_tulostiedot = None

    @staticmethod
    def get_raw_soup(link):
        r = requests.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def make_soup_osingot(self):
        self.soup_osingot = self.get_raw_soup(self.url_osingot)

    def make_soup_kurssi(self):
        self.soup_kurssi = self.get_raw_soup(self.url_kurssi)

    def make_soup_tulostiedot(self):
        self.soup_tulostiedot = self.get_raw_soup(self.url_tulostiedot)

    @staticmethod
    def pretty_val_st(v, expected_type, c_id=None):
        """ expected_type can be:
                int, float, str, date
            if there is a need:
                handle more string replacements (like miljard, etc.)
        """
        exception_str = \
            "c_id: {}; Unexpected type: expected_type:[{}], value:[{}]".format(
                c_id, expected_type, v
            )
        if not isinstance(expected_type, type):
            raise ScrapeException(exception_str)
        if expected_type != str and isinstance(v, expected_type):
            return v
        if expected_type != str and not v:
            raise ScrapeException(exception_str)

        if expected_type == int or expected_type == float:
            if isinstance(v, str) and v.strip() == "-":
                return None
            coefficient = 1
            if not isinstance(v, int) and not isinstance(v, float):
                v = v.lower().replace("?", "")
                v = v.replace("€", "").replace("eur", "")
                # remove noncompatibel characters in unicode (\x80-\xFF):
                v = re.sub(r'[^\x00-\x7F]+','', v)
                v = v.replace("\x00", "") # Remove empty character
                if "milj." in v:
                    coefficient *= 1e6
                    v = v.replace("milj.", "")
                v = v.strip()
            if v == "" or v == "-":
                return None
            try:
                v = float(v) * coefficient
            except ValueError:
                #print("[{}]".format(v))
                if "," in v:
                    v = float(v.replace(".", "").replace(",", ".")) \
                            * coefficient
                else:
                    raise ScrapeException(exception_str)
            if expected_type == int:
                try:
                    v_float = v
                    v = int(v)
                except ValueError:
                    raise ScrapeException(exception_str)
                if v != v_float:
                    raise ScrapeException(exception_str)
        elif expected_type == str:
            if v == None:
                v = ""
            else:
                try:
                    v = str(v).strip().lower()
                    # possible confusing in string
                    v = v.replace("\"", "").replace("'", "")
                    # the scandinavian letters:
                    # TODO: Is this needed? Test if no problems.
                    v = v.replace("\xe4", "a").replace("\xe5", "a")
                    v = v.replace("\xf6", "o")
                    # remove noncompatibel characters in unicode (\x80-\xFF):
                    len_v = len(v)
                    v = re.sub(r'[^\x00-\x7F]+','', v)
                    if len_v != len(v):
                        pass
                        # TODO: Fix this
                        #raise ScrapeException("Weird character(s)!")
                except ValueError:
                    raise ScrapeException(exception_str)
            if v == "-":
                v = ""
        elif expected_type == date:
            v = v.strip()
            if date_pattern_1.match(v): # DD.MM.YYYY
                dd, mm, yyyy = v.split(".")
                if int(dd) > 31 or int(mm) > 12 or \
                  int(dd) < 1 or int(mm) < 1 or int(yyyy) < 1:
                    raise ScrapeException(exception_str)
                v = "{}-{}-{}".format(yyyy, mm, dd) # YYYY-MM-DD
            elif not date_pattern_0.match(v): # YYYY-MM-DD
                raise ScrapeException(exception_str)
        else:
            raise ScrapeException(
                "Not an accepted type: [{}]".format(expected_type)
            )
        return v

    def pretty_val(self, v, expected_type):
        return self.pretty_val_st(v, expected_type, self.company_id)


    def scrape(self):
        self.metrics["scrape_date"] = date.today().strftime(date_format)

        self.metrics["osingot"] = self.get_osingot()

        self.metrics["kurssi"] = self.get_kurssi()
        self.metrics["kuvaus"] = self.get_kuvaus()
        self.metrics["perustiedot"] = self.get_perustiedot()
        self.metrics["tunnuslukuja"] = self.get_tunnuslukuja()

        self.metrics["toiminnan_laajuus"] = self.get_toiminnan_laajuus()
        self.metrics["kannattavuus"] = self.get_kannattavuus()
        self.metrics["vakavaraisuus"] = self.get_vakavaraisuus()
        self.metrics["maksuvalmius"] = self.get_maksuvalmius()
        self.metrics["sijoittajan_tunnuslukuja"] = \
            self.get_sijoittajan_tunnuslukuja()

        return self.metrics


    def get_osingot(self):
        try:
            if not self.soup_osingot:
                self.make_soup_osingot()
    
            table_tags = self.soup_osingot.find_all('table')
            table_row_tags = table_tags[5].find_all('tr')
            head = ["vuosi", "irtoaminen", "oikaistu_euroina", \
                    "maara", "valuutta", "tuotto_%", "lisatieto"]
            osingot = {}
            row_counter = 0
            for row in table_row_tags:
                sub_dict = {}
                columns = row.find_all('td')
                # if every metric (except "lisatieto") is empty it can be discarded
                if not columns[0].string:
                    for i in range(1,6):
                        if columns[i].string:
                            raise ScrapeException("Unexpected osinko row")
                    continue
                for i in range(7):
                    val = columns[i].string
                    if i == 0:
                        val = self.pretty_val(val, int)
                    elif i == 1:
                        if val is not None:
                            val = self.pretty_val(val, date)
                    elif i == 2 or i == 3 or i == 5:
                        if val is not None:
                            val = self.pretty_val(val, float)
                    elif i == 4 or i == 6:
                        val = self.pretty_val(val, str)
                    sub_dict[head[i]] = val
                osingot[str(row_counter)] = sub_dict
                row_counter += 1
            return osingot
        except:
            traceback.print_exc()
            return "FAIL"


    def get_kurssi(self):
        try:
            if not self.soup_kurssi:
                self.make_soup_kurssi()
    
            table_tags = self.soup_kurssi.find_all('table')
            kurssi = table_tags[5].find('span').text
            kurssi = self.pretty_val(kurssi, float)
            return kurssi
        except:
            traceback.print_exc()
            return "FAIL"

    def get_kuvaus(self):
        try:
            if not self.soup_kurssi:
                self.make_soup_kurssi()
    
            class_padding_tags = self.soup_kurssi.find_all(class_="paddings")
            kuvaus = None
            for tag in class_padding_tags:
                if tag.parent.h3.text == "Yrityksen perustiedot":
                    kuvaus = tag.p.text.strip().replace("\n"," ").replace("\r"," ")
                    kuvaus = self.pretty_val(kuvaus, str)
            if not kuvaus:
                raise ScrapeException("Kuvaus not found")
            return kuvaus
        except:
            traceback.print_exc()
            return "FAIL"

    def get_perustiedot(self):
        try:
            if not self.soup_kurssi:
                self.make_soup_kurssi()
    
            class_is_TSBD = self.soup_kurssi.find_all(class_="table_stock_basic_details")
            perustiedot = {}
            perustiedot_tag = None
            for tag in class_is_TSBD:
                if tag.parent.parent.h3.text.strip() == "Osakkeen perustiedot":
                    perustiedot_tag = tag
                    break
            tr_tags = perustiedot_tag.find_all('tr')
            c = 0
            for i in tr_tags:
                td_tags = i.find_all('td')
                if c == 0:
                    key = td_tags[0].text.replace(":","")
                    val = td_tags[1].text
                    perustiedot[self.pretty_val(key, str)] = self.pretty_val(val, str)
    
                    strs = td_tags[2].text.split("\n")
                    [key, val] = strs[1].split(":")
                    perustiedot[self.pretty_val(key, str)] = self.pretty_val(val, str)
    
                    [key, val] = strs[2].split(":")
                    perustiedot[self.pretty_val(key, str)] = self.pretty_val(val, str)
                    c += 1
                else:
                    key = td_tags[0].text.strip().replace(":","")
                    val = td_tags[1].text.strip()
                    key = self.pretty_val(key, str)
                    if key == "osakkeet":
                        key = "{}_kpl".format(key)
                        val = val.replace("kpl","").replace("\xa0", "")
                        val = self.pretty_val(val, int)
                    elif key == "markkina-arvo":
                        val = self.pretty_val(val, float)
                    elif key == "listattu":
                        val = self.pretty_val(val, date)
                    elif key == "isin-koodi" or key == "porssi" or \
                                key == "nimellisarvo":
                        val = self.pretty_val(val, str)
                    elif key == "kaupank. val.":
                        key = "kaupankaynti_valuutta"
                        val = self.pretty_val(val, str)
                    else:
                        raise ScrapeException(
                            "Unrecognized key: {}, val: {}".format(key, val)
                        )
                    perustiedot[key] = val
            return perustiedot
        except:
            traceback.print_exc()
            return "FAIL"

    def get_tunnuslukuja(self):
        # The tunnuslukuja field is missing on many companies.
        # This is not an fail, but means that the company is probably smaller,
        # because Kauppalehti does not provide the most updated tunnuslukuja
        # of the company.
        try:
            if not self.soup_kurssi:
                self.make_soup_kurssi()
    
            table_tags = self.soup_kurssi.find_all('table')
            tunnuslukuja = {}
            tunnuslukuja_tag = None
            for tag in table_tags:
                if tag.parent.p and tag.parent.p.text.strip() == "Tunnuslukuja":
                    tunnuslukuja_tag = tag
                    break
            if not tunnuslukuja_tag:
                logger.debug("c_id: {}; NO tunnuslukuja".format(self.company_id))
                return None
            tr_tags = tunnuslukuja_tag.find_all('tr')
            head = [
                "viimeisin_kurssi_eur",
                "tulos/osake",
                "oma_paaoma/osake_eur",
                "p/e-luku_reaali",
                "osinko/osake_eur",
                "markkina-arvo_eur"
            ]
            c = 0
            for i in tr_tags:
                td_tags = i.find_all('td')
                if c == 0:
                    strs = td_tags[0].text.split("(")
                    #key = strs[0].strip() # key could be used for debuging
                    val = strs[1].replace(")","")
                else:
                    #key = td_tags[0].text
                    val = td_tags[1].text
                if val:
                    val = self.pretty_val(val, float)
                tunnuslukuja[head[c]] = val
                c += 1
            return tunnuslukuja
        except:
            traceback.print_exc()
            return "FAIL"


    def get_tulostiedot(self, header, head=None):
        try:
            if head:
                assert isinstance(head, list), "Invalid head type: {}".format(type(head))
                for s in head:
                    assert isinstance(s, str), "Invalid name type: {}".format(type(s))
    
            if not self.soup_tulostiedot:
                self.make_soup_tulostiedot()
    
            table_tags = self.soup_tulostiedot.find_all(class_="table_stockexchange")
            tulostiedot = {}
            tulostiedot_tag = None
            for tag in table_tags:
                if tag.parent.h3 and tag.parent.h3.text.strip().lower() == header.lower():
                    tulostiedot_tag = tag
                    break
            if not tulostiedot_tag:
                logger.debug("c_id: {}; NO {}".format(self.company_id, header))
                return None
            tr_tags = tulostiedot_tag.find_all('tr')
            # Go trough rows, and store them before populating tulostiedot.
            type_row_list = []
            r = 0 # row counter
            for i in tr_tags:
                td_tags = i.find_all('td')
                type_row = []
                c = 0 # column counter
                for j in td_tags:
                    if c == 0 or r == 0:
                        val = self.pretty_val(j.text, str)
                    else:
                        val = self.pretty_val(j.text, float)
                    type_row.append(val)
                    c += 1
                r += 1
                type_row_list.append(type_row)
            # Reorganize data
            row_count = len(type_row_list)
            col_count = len(type_row_list[0])
            if head:
                assert len(head) == row_count - 1, \
                    "c_id: {}; Expected rows: {}; Got: {}".format(
                        self.company_id, len(head), row_count - 1
                    )
            # type_row_list[0] is like: "12/16"
            for col in range(1, col_count):
                if type_row_list[0][col].strip():
                    sub_dict = {}
                    for row in range(1, row_count):
                        if head:
                            sub_dict[head[row - 1]] = type_row_list[row][col]
                        else:
                            sub_dict[type_row_list[row][0]] = type_row_list[row][col]
                    tulostiedot[self.pretty_val(type_row_list[0][col], str)] = sub_dict
            return tulostiedot
        except:
            traceback.print_exc()
            return "FAIL"

    def get_toiminnan_laajuus(self):
        head = [
            "liikevaihto",
            "liikevaihdon_muutos_%",
            "ulkomaantoiminta_%",
            "oikaistun_taseen_loppusumma",
            "investoinnit",
            "investointiaste_%",
            "henkilosto_keskimaarin"
        ]
        return self.get_tulostiedot("toiminnan laajuus", head)

    def get_kannattavuus(self):
        head = [
            "kayttokate",
            "liiketulos",
            "nettotulos",
            "kokonaistulos",
            "sijoitetun_paaoman_tuotto_%",
            "oman_paaoman_tuotto_%",
            "kokonaispaaoman_tuotto_%"
        ]
        return self.get_tulostiedot("kannattavuus", head)

    def get_vakavaraisuus(self):
        head = [
            "omavaraisuusaste_%",
            "nettovelkaantumisaste_%",
            "korollinen_nettovelka",
            "nettorahoitus_kulut/liikevaihto_%",
            "nettorahoitus_kulut/kayttokate_%",
            "vieraan_paaoman_takaisin_maksuaika"
        ]
        return self.get_tulostiedot("vakavaraisuus", head)

    def get_maksuvalmius(self):
        head = [
            "quick_ratio",
            "current_ratio",
            "likvidit_varat"
        ]
        return self.get_tulostiedot("maksuvalmius", head)

    def get_sijoittajan_tunnuslukuja(self):
        head = [
            "markkina-arvo_(p)",
            "tasesubstanssi_ilman_vahennettya_osinkoa_(b)",
            "yritysarvo_(ev)",
            "tulos_(e)",
            "p/b-luku",
            "p/s-luku",
            "p/e-luku",
            "ev/ebit-luku",
            "tulos/osake_(eps)_euroa",
            "tulorahoitus/osake (cps)_euroa",
            "oma_paaoma/osake_euroa",
            "osinko/kokonaistulos_%"
        ]
        return self.get_tulostiedot("sijoittajan tunnuslukuja", head)
