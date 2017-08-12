import requests, re, logging
from bs4 import BeautifulSoup
from datetime import date
from threading import Thread

logger = logging.getLogger('root')


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"

date_format = "%Y-%m-%d" # YYYY-MM-DD
date_short_format = "%y-%m-%d" # YY-MM-DD
datetime_format = "%y-%m-%d_%H-%M-%S" # YY-MM-DD_HH-MM-SS: for filename
date_pattern_0 = re.compile("^\d{4}\-\d{2}\-\d{2}$") # YYYY-MM-DD
date_pattern_1 = re.compile("^\d{2}\.\d{2}\.\d{4}$") # DD.MM.YYYY


class ScrapeException(Exception):
    pass


class scrapeCompanyThread(Thread):
    def __init__(self, company_id, company_name, company_list,
                 company_failed_count, thread_index=-1):
        Thread.__init__(self)
        assert isinstance(company_id, int)
        assert isinstance(company_name, str)
        self.company_id = company_id
        self.company_name = company_name
        self.company_list = company_list
        self.company_failed_count = company_failed_count
        self.name = "({}, {}, {})".format(thread_index, self.company_id, self.company_name)

    def __repr__(self):
        return "scrapeCompanyThread({})".format(self.name)

    def run(self):
        #logger.debug("Starting {}".format(self))
        company = Company(c_id=self.company_id, c_name=self.company_name)
        try:
            company.scrape()
            self.company_list.append(company)
            #logger.debug("Finished {}".format(self))
        except ScrapeException:
            self.company_failed_count += 1
            logger.error("Failed   {}".format(self))


def scrape_companies(company_names, company_list, company_failed_count):
    assert isinstance(company_names, dict), "Invalid company_names"
    assert len(company_names) > 0, "No company_names"
    assert company_list == [], "Invalid company_list"
    assert company_failed_count == 0, "Invalid company_failed_count"
    thread_list = []
    thread_index = 1
    for company_id in company_names:
        thread = scrapeCompanyThread(company_id, company_names[company_id],
                                     company_list, company_failed_count, thread_index)
        thread_list.append(thread)
        thread.start()
        thread_index += 1
    for thread in thread_list:
        thread.join()


class Company():
    def __init__(self, c_metrics=None, c_id=None, c_name=None):
        assert c_metrics or (c_id and c_name), "Invalid Company input"
        if c_metrics:
            assert isinstance(c_metrics, dict)
            assert not c_id
            assert not c_name
            self.metrics = c_metrics
            self.company_id = self.metrics["company_id"]
            self.company_name = self.metrics["company_name"]

            self.do_calculations()
            self.set_representative_strings()
        else:
            assert not c_metrics
            self.metrics = {}
            self.company_id = c_id
            self.company_name = c_name
        assert self.company_id
        assert isinstance(self.company_id, int)
        assert isinstance(self.company_name, str)

        self.json_metrics = None # for storage

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
        #self.metrics["tunnuslukuja"] = self.dict_to_pretty_dict(get_tunnuslukuja_OLD(url_ku)) # TODO: Remove when replacement tested!
        self.metrics["tunnuslukuja"] = get_tunnuslukuja(url_ku)

        toiminnan_laajuus = get_kurssi_tulostiedot(url_ku_tu, "Toiminnan laajuus")
        kannattavuus = get_kurssi_tulostiedot(url_ku_tu, "Kannattavuus")
        vakavaraisuus = get_kurssi_tulostiedot(url_ku_tu, "Vakavaraisuus")
        maksuvalmius = get_kurssi_tulostiedot(url_ku_tu, "Maksuvalmius")
        sijoittajan_tunnuslukuja = get_kurssi_tulostiedot(url_ku_tu, "Sijoittajan tunnuslukuja")

        self.metrics["toiminnan_laajuus"] = self.list_to_pretty_dict_pivot(toiminnan_laajuus)
        self.metrics["kannattavuus"] = self.list_to_pretty_dict_pivot(kannattavuus)
        self.metrics["vakavaraisuus"] = self.list_to_pretty_dict_pivot(vakavaraisuus)
        self.metrics["maksuvalmius"] = self.list_to_pretty_dict_pivot(maksuvalmius)
        self.metrics["sijoittajan_tunnuslukuja"] = self.list_to_pretty_dict_pivot(sijoittajan_tunnuslukuja)

        self.json_metrics = "\n{}".format(self.metrics)

    @staticmethod
    def make_value_pretty(v):
        # substitute string for coefficient
        coefficient = 1
        if "milj.eur" in v:
            coefficient = 1e6
            v = v.replace("milj.eur", "")
        try:
            v = float(v) * coefficient
        except ValueError:
            pass
        # integer
        try:
            if v == int(v):
                v = int(v)
        except ValueError:
            pass
        # TODO: handle other like miljard, etc.
        # TODO: turn all empty fields to "-"
        # TODO: handle dates and booleans
        return v

    @staticmethod
    def list_to_pretty_dict(list_in):
        d = {}
        head = list_in[1]
        for i in range(2, len(list_in)):
            sub_d = {}
            for j in range(len(head)):
                k = str(head[j]).lower()
                v = str(list_in[i][j]).lower()
                sub_d[k] = Company.make_value_pretty(v)
            d[str(i-2)] = sub_d
        return d

    @staticmethod
    def list_to_pretty_dict_pivot(list_in):
        l = []
        head = list_in[1]
        first_col = str(head[0]).lower() # "vuosi"
        for i in range(2, len(list_in)):
            sub_d = {}
            for j in range(len(head)):
                k = str(head[j]).lower()
                v = str(list_in[i][j]).lower()
                sub_d[k] = Company.make_value_pretty(v)
            l.append(sub_d)
        d = {}
        for k in head:
            k = str(k).lower()
            if k != first_col and k != "-":
                sub_d = {}
                for row_d in l:
                    sub_d[row_d[first_col]] = row_d[k]
                d[k] = sub_d
        return d

    @staticmethod
    def dict_to_pretty_dict(dict_in):
        d = {}
        for i in dict_in:
            if i != 0:
                k = str(i).lower()
                v = str(dict_in[i]).lower()
                d[k] = Company.make_value_pretty(v)
        return d

    def add_dict_to_str(self, in_dict, in_str="", indent_str="", simple=False):
        max_key_len = 0
        for key in in_dict:
            if len(key) > max_key_len:
                max_key_len = len(key)

        line_str = "\n" + indent_str + "{:" + str(max_key_len) + "} : {}"
        next_indent_str = indent_str + "\t"

        for key in sorted(in_dict):
            val_type = type(in_dict[key])
            if val_type == dict and not simple:
                in_str += line_str.format(key, "{")
                in_str = self.add_dict_to_str(in_dict[key], in_str, next_indent_str)
                in_str += "\n" + indent_str + "}"
            else:
                line = line_str.format(key, str(in_dict[key]))
                in_str += line[:80]
                if len(line) > 80:
                    in_str += "..."
        return in_str

    def set_representative_strings(self):
        assert "calculations" in self.metrics
        self.str_metrics = self.add_dict_to_str(self.metrics)
        self.str_metrics_simple = self.add_dict_to_str(self.metrics, simple=True)
        self.str_calculations = self.add_dict_to_str(self.metrics["calculations"])

    def do_calculations(self):
        self.metrics["calculations"] = {}
        self.calculate_osinko()
        self.collect_metrics()
        self.calculate_fresh()

    def addCalc(self, key, value):
        assert not str(key) in self.metrics["calculations"]
        self.metrics["calculations"][str(key)] = value

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

    def set_taloustiedot_current_key(self):
        self.tt_current_key = None # "12/16", used for dictionaries scraped from the tulostiedot-page
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
        assert self.tt_current_key == "12/16"

    def collect_metrics(self):
        # Sidenote: not using: toiminnan laajuus, maksuvalmius
        self.set_taloustiedot_current_key() # self.tt_current_key
        self.addCalc("tt_current_key", self.tt_current_key)

        self.addCalc("company_id", self.metrics["company_id"])
        self.addCalc("company_name", self.metrics["company_name"])
        self.addCalc("kurssi", self.metrics["kurssi"])
        self.addCalc("kuvaus", self.metrics["kuvaus"])
        self.addCalc("scrape_date", self.metrics["scrape_date"])

        self.addCalc("toimiala", self.metrics["perustiedot"]["toimiala"])
        self.addCalc("toimialaluokka", self.metrics["perustiedot"]["toimialaluokka"])
        self.addCalc("osakkeet_kpl", self.metrics["perustiedot"]["osakkeet_kpl"])

        self.addCalc("ROE", self.metrics["kannattavuus"][self.tt_current_key]["oman paaoman tuotto, %"])
        self.addCalc("nettotulos", self.metrics["kannattavuus"][self.tt_current_key]["nettotulos"])

        self.addCalc("omavaraisuusaste", self.metrics["vakavaraisuus"][self.tt_current_key]["omavaraisuusaste, %"])
        self.addCalc("gearing", self.metrics["vakavaraisuus"][self.tt_current_key]["nettovelkaantumisaste, %"])

        self.addCalc("PB", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["p/b-luku"])
        self.addCalc("PE", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["p/e-luku"])
        self.addCalc("E", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["tulos (e)"])
        self.addCalc("P", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["markkina-arvo (p)"])

    def calculate_fresh(self):
        calc = self.metrics["calculations"]
        current_year = date.today().strftime("%Y") # "YYYY"
        # the metrics below are fresher, because they are calculated with the current stock price
        self.addCalc("calc_osinkotuotto_percent", round( 100 * calc["osinko_euro"][current_year] / calc["kurssi"], 2))
        self.addCalc("calc_P", round( calc["osakkeet_kpl"] * calc["kurssi"] / 1e6, 4))
        self.addCalc("calc_P_factor", round( calc["calc_P"] / calc["P"], 4))
        self.addCalc("calc_PB", round( calc["calc_P_factor"] * calc["PB"], 2))
        self.addCalc("calc_PE", round( calc["calc_P_factor"] * calc["PE"], 2))


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
    exception_str = "Unexpected type: expected_type:[{}], value:[{}]".format(expected_type, v)
    if not isinstance(expected_type, type):
        raise ScrapeException(exception_str)
    if expected_type != str and isinstance(v, expected_type):
        return v
    if expected_type != str and not v:
        raise ScrapeException(exception_str)

    if expected_type == int or expected_type == float:
        coefficient = 1
        if not isinstance(v, int) and not isinstance(v, float):
            v = v.lower().replace("€", "").replace("eur", "")
            # remove noncompatibel characters in unicode (\x80-\xFF):
            v = re.sub(r'[^\x00-\x7F]+','', v)
            if "milj." in v:
                coefficient *= 1e6
                v = v.replace("milj.", "")
        try:
            v = float(v) * coefficient
        except ValueError:
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
                # the scandinavian letters:
                v = v.replace("\xe4", "a").replace("\xe5", "a").replace("\xf6", "o")
                # remove noncompatibel characters in unicode (\x80-\xFF):
                len_v = len(v)
                v = re.sub(r'[^\x00-\x7F]+','', v)
                if len_v != len(v):
                    raise ScrapeException("Weird character(s)!")
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
        raise ScrapeException("Not an accepted type: [{}]".format(expected_type))
    return v


def fix_str_OLD(string): # TODO: Remove later
    # deals with scandinavian characters
    return string.replace("\xe4", "a").replace("\xe5", "a").replace("\xf6", "o")

def fix_str_noncompatible_chars_in_unicode(string): # TODO: Remove later
    return string.replace("\x9a","?").replace("\x96","?").replace("\x92","?")


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
            raise ScrapeException("Unexpected: id:[{}], name:[{}]".format(company_id, company_name))
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
                raise ScrapeException("Unrecognized key: {}, val: {}".format(key, val))
            perustiedot[key] = val
    return perustiedot

# TODO: Go trough old functions here under and write tests for them
# USE FUNCTION: pretty_val()


# TODO: Run all tests and remove OLD-function.
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

""" TODO: Remove when replacement tested!
def get_tunnuslukuja_table_TAG(url):
    soup = get_raw_soup(url)
    try:
        table_tags=soup.find_all('table')
        
        for tag in table_tags:
            try:
                if tag.parent.p.text.strip() == "Tunnuslukuja":
                    return tag
            except:
                pass
        logger.debug("tunnuslukuja_table_TAG EI LOYTYNYT")
    except:
        logger.debug("tunnuslukuja_table_TAG")
    return -1

def get_tunnuslukuja_OLD(url):
    tunnuslukuja_dict={}
    try:
        TAG=get_tunnuslukuja_table_TAG(url)
        
        if TAG == -1:
            tunnuslukuja_dict[0]=False
            return tunnuslukuja_dict
        
        tr_tags=TAG.find_all('tr')
        c=0
        for i in tr_tags:
            td_tags=i.find_all('td')
            
            if c==0:
                strs=td_tags[0].text.split("(")
                key=strs[0].strip()
                val=strs[1].replace(")","")
            else:
                key=td_tags[0].text
                val=td_tags[1].text
            
            if c==3:
                try:
                    val=float(val)
                except:
                    logger.debug("float({})".format(key))
            elif c==5:
                try:
                    parts=val.split()
                    val=float(parts[0])
                    k=parts[1].split(".")
                    key=key + " ({}. EUR)".format(k[0])
                except:
                    logger.debug("float({})".format(key))
            else:
                try:
                    parts=val.split()
                    val=float(parts[0])
                    key=key + " (EUR)"
                except:
                    logger.debug("float({})".format(key))
            
            tunnuslukuja_dict[fix_str_OLD(key)]=val
            c+=1
        
        tunnuslukuja_dict[0]=True
    except:
        logger.debug("tunnuslukuja_dict")
        tunnuslukuja_dict[0]=False
    return tunnuslukuja_dict
"""

""" get_kurssi_tulostiedot usecase:

toiminnan_laajuus = get_kurssi_tulostiedot(url_ku_tu, "Toiminnan laajuus")
kannattavuus = get_kurssi_tulostiedot(url_ku_tu, "Kannattavuus")
vakavaraisuus = get_kurssi_tulostiedot(url_ku_tu, "Vakavaraisuus")
maksuvalmius = get_kurssi_tulostiedot(url_ku_tu, "Maksuvalmius")
sijoittajan_tunnuslukuja = get_kurssi_tulostiedot(url_ku_tu, "Sijoittajan tunnuslukuja")

"""


def get_tulostiedot(url, header):
    tulostiedot = {}
    soup = get_raw_soup(url)
    table_tags = soup.find_all(class_="table_stockexchange")
    tulostiedot_tag = None
    for tag in table_tags:
        if tag.parent.h3 and tag.parent.h3.text.strip() == header:
            tulostiedot_tag = tag
            break
    tr_tags = tulostiedot_tag.find_all('tr')
    # HERE
    r = 0 # row
    for i in tr_tags:
        td_tags = i.find_all('td')
        rivi = []
        c = 0 # column
        for j in td_tags:
            if r == 0:
                rivi.append("VUOSI")
                r += 1
            else:
                if c == 0:
                    val = pretty_val(j.text, str)
                else:
                    val = pretty_val(j.text, float)
                rivi.append(val)
        tulostiedot[pretty_val(i, str)] = rivi
    return tulostiedot



def get_KURSSI_TULOSTIEDOT_table_TAG(url, otsikko):
    soup = get_raw_soup(url)
    try:
        table_tags=soup.find_all(class_="table_stockexchange")
        
        for tag in table_tags:
            try:
                if tag.parent.h3.text.strip() == otsikko:
                    return tag
            except:
                pass
        logger.debug("Otsikko='{}' TAG EI LOYTYNYT".format(otsikko))
    except:
        logger.debug("Otsikko='{}'".format(otsikko))
    return -1

# OLD
def get_kurssi_tulostiedot(url, otsikko):
    matrix=["NOT REDY"]
    try:
        TAG = get_KURSSI_TULOSTIEDOT_table_TAG(url, otsikko)
        
        if TAG == -1:
            matrix[0]=False
            return matrix
        
        tr_tags=TAG.find_all('tr')
        r=0 #rivi
        for i in tr_tags:
            td_tags=i.find_all('td')
            
            rivi=[]
            for j in td_tags:
                if r==0:
                    rivi.append("VUOSI")
                    r+=1
                else:
                    val=fix_str_OLD(j.text.strip())
                    try:
                        val=float(val.replace("\xa0",""))
                    except:
                        pass
                        # logger.debug("Otsikko='{}', float('{}')".format(otsikko, val))
                    rivi.append(val)
            
            matrix.append(rivi)
        
        matrix[0]=True
    except:
        logger.debug("Otsikko='{}'".format(otsikko))
        matrix[0]=False

    return matrix
