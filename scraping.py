import requests, re, logging
from bs4 import BeautifulSoup
from datetime import date
from multiprocessing import Process, Queue
import json

logger = logging.getLogger('root')


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
    try:
        company = Company(c_id=company_id, c_name=company_name)
        company.scrape()
        queue.put(company.metrics)
    except:
        queue.put( {"company_id": company_id, "company_name": company_name} )

def scrape_companies_with_processes(company_names, showProgress=True):
    metrics_queue = Queue() # Company.metrics dicts are stored here
    # TODO: Could use Pool instead of process_list.
    #  Would the code be simpler? Performance?
    process_list = []
    for company_id in company_names:
        process = Process(
            target=scrape_company_target_function,
            args=(metrics_queue, company_id, company_names[company_id]),
            name="({}, {})".format(company_id, company_names[company_id])
        )
        process_list.append(process)

    for process in process_list:
        logger.debug("Starting {}".format(process))
        process.start()

    metrics_list = []
    all_c = len(company_names) # all companies expected count
    c = 0 # counter for len(metrics_list)
    while True:
        if len(metrics_list) == all_c:
            break
        # .get() waits on the next value.
        # Then .join() is not needed for processes.
        metrics_list.append(metrics_queue.get())
        if showProgress:
            c += 1
            if c%5 == 0:
                logger.info("\t{:3}/{} - {:2}%".format(
                    c, all_c, round( 100*c/all_c )
                ))

    return metrics_list


class Company():
    def __init__(self, c_metrics=None, c_id=None, c_name=None):
        assert c_metrics or (c_id and c_name), "Invalid Company input"
        if c_metrics:
            assert isinstance(c_metrics, dict)
            assert not c_id
            assert not c_name
            self.metrics = c_metrics
            self.calculations = {}
            self.company_id = self.metrics["company_id"]
            self.company_name = self.metrics["company_name"]

            if len(self.metrics) > 2:
                self.do_calculations()
        else:
            assert not c_metrics
            self.metrics = {}
            self.calculations = {}
            self.company_id = c_id
            self.company_name = c_name.replace("\"", "").replace("'", "")
        assert self.company_id
        assert isinstance(self.company_id, int)
        assert isinstance(self.company_name, str)

    def __repr__(self):
        return "Company({}, {})".format(self.company_id, self.company_name)

    def scrape(self):
        url_os = osingot_yritys_url.format(self.company_id)
        url_ku = kurssi_url.format(self.company_id)
        url_ku_tu = kurssi_tulostiedot_url.format(self.company_id)

        self.metrics["company_id"] = self.company_id
        self.metrics["company_name"] = self.company_name
        self.metrics["scrape_date"] = date.today().strftime(date_format)

        self.metrics["kurssi"] = get_kurssi(url_ku)
        self.metrics["kuvaus"] = get_kuvaus(url_ku)

        self.metrics["osingot"] = get_osingot(url_os)

        self.metrics["perustiedot"] = get_perustiedot(url_ku)
        self.metrics["tunnuslukuja"] = get_tunnuslukuja(url_ku)

        self.metrics["toiminnan_laajuus"] = get_toiminnan_laajuus(url_ku_tu)
        self.metrics["kannattavuus"] = get_kannattavuus(url_ku_tu)
        self.metrics["vakavaraisuus"] = get_vakavaraisuus(url_ku_tu)
        self.metrics["maksuvalmius"] = get_maksuvalmius(url_ku_tu)
        self.metrics["sijoittajan_tunnuslukuja"] = \
            get_sijoittajan_tunnuslukuja(url_ku_tu)

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

    def do_calculations(self):
        self.calculate_osinko()
        self.collect_metrics()
        self.calculate_fresh()


def get_raw_soup(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

def pretty_val(v, expected_type):
    """ expected_type can be:
            int, float, str, date
        if there is a need:
            handle more string replacements (like miljard, etc.)
    """
    exception_str = "Unexpected type: expected_type:[{}], value:[{}]".format(
        expected_type, v
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
            v = v.lower().replace("€", "").replace("eur", "")
            # remove noncompatibel characters in unicode (\x80-\xFF):
            v = re.sub(r'[^\x00-\x7F]+','', v)
            v = v.replace("\x00", "") # Remove empty character
            if "milj." in v:
                coefficient *= 1e6
                v = v.replace("milj.", "")
        try:
            v = float(v) * coefficient
        except ValueError:
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

def scrape_company_names():
    soup = get_raw_soup(osingot_url)
    form_tags = soup.find_all('form')
    option_tags = form_tags[2].find_all('option')
    company_names = {}
    for i in option_tags:
        company_id = i.attrs['value']
        company_name = i.string
        if company_id and company_name:
            company_id = int(company_id)
            company_name = pretty_val(company_name, str)
            company_names[company_id] = company_name
        elif company_name != "Valitse osake":
            raise ScrapeException(
                "Unexpected: id:[{}], name:[{}]".format(
                    company_id, company_name
                )
            )
    return company_names

def get_kurssi(url):
    soup = get_raw_soup(url)
    table_tags = soup.find_all('table')
    kurssi = table_tags[5].find('span').text
    kurssi = pretty_val(kurssi, float)
    return kurssi

def get_kuvaus(url):
    soup = get_raw_soup(url)
    class_padding_tags = soup.find_all(class_="paddings")
    kuvaus = None
    for tag in class_padding_tags:
        if tag.parent.h3.text == "Yrityksen perustiedot":
            kuvaus = tag.p.text.strip().replace("\n"," ").replace("\r"," ")
            kuvaus = pretty_val(kuvaus, str)
    if not kuvaus:
        raise ScrapeException("Kuvaus not found")
    return kuvaus

def get_osingot(url):
    soup = get_raw_soup(url)
    table_tags = soup.find_all('table')
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
                val = pretty_val(val, int)
            elif i == 1:
                val = pretty_val(val, date)
            elif i == 2 or i == 3 or i == 5:
                val = pretty_val(val, float)
            elif i == 4 or i == 6:
                val = pretty_val(val, str)
            sub_dict[head[i]] = val
        osingot[str(row_counter)] = sub_dict
        row_counter += 1
    return osingot

def get_perustiedot(url):
    perustiedot = {}
    soup = get_raw_soup(url)
    class_is_TSBD = soup.find_all(class_="table_stock_basic_details")
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
            perustiedot[pretty_val(key, str)] = pretty_val(val, str)

            strs = td_tags[2].text.split("\n")
            [key, val] = strs[1].split(":")
            perustiedot[pretty_val(key, str)] = pretty_val(val, str)

            [key, val] = strs[2].split(":")
            perustiedot[pretty_val(key, str)] = pretty_val(val, str)
            c += 1
        else:
            key = td_tags[0].text.strip().replace(":","")
            val = td_tags[1].text.strip()
            key = pretty_val(key, str)
            if key == "osakkeet":
                key = "{}_kpl".format(key)
                val = val.replace("kpl","").replace("\xa0", "")
                val = pretty_val(val, int)
            elif key == "markkina-arvo":
                val = pretty_val(val, float)
            elif key == "listattu":
                val = pretty_val(val, date)
            elif key == "isin-koodi" or key == "porssi" or \
                        key == "nimellisarvo":
                val = pretty_val(val, str)
            elif key == "kaupank. val.":
                key = "kaupankaynti_valuutta"
                val = pretty_val(val, str)
            else:
                raise ScrapeException(
                    "Unrecognized key: {}, val: {}".format(key, val)
                )
            perustiedot[key] = val
    return perustiedot

def get_tunnuslukuja(url):
    tunnuslukuja = {}
    soup = get_raw_soup(url)
    table_tags = soup.find_all('table')
    tunnuslukuja_tag = None
    for tag in table_tags:
        if tag.parent.p and tag.parent.p.text.strip() == "Tunnuslukuja":
            tunnuslukuja_tag = tag
            break
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
        tunnuslukuja[head[c]] = pretty_val(val, float)
        c += 1
    return tunnuslukuja


def get_tulostiedot(url, header, head=None):
    if head:
        assert isinstance(head, list), "Invalid head type: {}".format(type(head))
        for s in head:
            assert isinstance(s, str), "Invalid name type: {}".format(type(s))
    tulostiedot = {}
    soup = get_raw_soup(url)
    table_tags = soup.find_all(class_="table_stockexchange")
    tulostiedot_tag = None
    for tag in table_tags:
        if tag.parent.h3 and tag.parent.h3.text.strip().lower() == header.lower():
            tulostiedot_tag = tag
            break
    if not tulostiedot_tag:
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
                val = pretty_val(j.text, str)
            else:
                val = pretty_val(j.text, float)
            type_row.append(val)
            c += 1
        r += 1
        type_row_list.append(type_row)
    # Reorganize data
    row_count = len(type_row_list)
    col_count = len(type_row_list[0])
    if head:
        assert len(head) == row_count - 1, "Wrong numer of names in head list."
    # type_row_list[0] is like: "12/16"
    for col in range(1, col_count):
        if type_row_list[0][col].strip():
            sub_dict = {}
            for row in range(1, row_count):
                if head:
                    sub_dict[head[row - 1]] = type_row_list[row][col]
                else:
                    sub_dict[type_row_list[row][0]] = type_row_list[row][col]
            tulostiedot[pretty_val(type_row_list[0][col], str)] = sub_dict
    return tulostiedot

def get_toiminnan_laajuus(url):
    head = [
        "liikevaihto",
        "liikevaihdon_muutos_%",
        "ulkomaantoiminta_%",
        "oikaistun_taseen_loppusumma",
        "investoinnit",
        "investointiaste_%",
        "henkilosto_keskimaarin"
    ]
    return get_tulostiedot(url, "toiminnan laajuus", head)

def get_kannattavuus(url):
    head = [
        "kayttokate",
        "liiketulos",
        "nettotulos",
        "kokonaistulos",
        "sijoitetun_paaoman_tuotto_%",
        "oman_paaoman_tuotto_%",
        "kokonaispaaoman_tuotto_%"
    ]
    return get_tulostiedot(url, "kannattavuus", head)

def get_vakavaraisuus(url):
    head = [
        "omavaraisuusaste_%",
        "nettovelkaantumisaste_%",
        "korollinen_nettovelka",
        "nettorahoitus_kulut/liikevaihto_%",
        "nettorahoitus_kulut/kayttokate_%",
        "vieraan_paaoman_takaisin_maksuaika"
    ]
    return get_tulostiedot(url, "vakavaraisuus", head)

def get_maksuvalmius(url):
    head = [
        "quick_ratio",
        "current_ratio",
        "likvidit_varat"
    ]
    return get_tulostiedot(url, "maksuvalmius", head)

def get_sijoittajan_tunnuslukuja(url):
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
    return get_tulostiedot(url, "sijoittajan tunnuslukuja", head)
