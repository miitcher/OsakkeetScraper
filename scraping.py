import requests, re, logging, traceback, time
from bs4 import BeautifulSoup
from datetime import date
from multiprocessing import Process, Queue
import scrape_logger

#logger = logging.getLogger('root')

level = "INFO"
#level = "DEBUG"
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
date_pattern_2 = re.compile("^\d{2}/\d{2}$")         # MM/YY


class ScrapeException(Exception):
    pass

class ScrapeNetworkException(Exception):
    pass

class ScrapeAgainFailedException(Exception):
    pass


def scrape_company_target_function(queue, company_id, company_name):
    # Used as target function for multitreading.Process
    scraper = Scraper(company_id)
    metrics = scraper.scrape()
    if company_name:
        assert metrics["company_name"][:3].lower() == company_name[:3].lower(), \
            "Scraped name: {}; Given name: {}".format(metrics["company_name"],
                                                      company_name)
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
        #logger.debug("Starting {}".format(process))
        process.start()

    metrics_list = []
    len_all = len(company_names)
    len_metrics_list = 0 # counter
    while True:
        if len_metrics_list == len_all:
            break
        # .get() waits on the next value.
        # Then .join() is not needed for processes.
        metrics = metrics_queue.get()
        assert isinstance(metrics, dict) and len(metrics) > 5, \
            "Failed metric: {}; len: {}".format(type(metrics), len(metrics))
        metrics_list.append(metrics)
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

        self.max_scrape_retries = 3
        self.wait_before_last_retry = 1 # seconds

    def define_expected_missing_metrics(self):
        self.exp_missing_metrics = []

        # The tulostiedot are missing for banks.
        missing_tulostiedot = [1971, 1970, 1105, 1104, 2056, 1083, 1089]
        if self.company_id in missing_tulostiedot:
            self.exp_missing_metrics.append("toiminnan_laajuus")
            self.exp_missing_metrics.append("kannattavuus")
            self.exp_missing_metrics.append("vakavaraisuus")
            self.exp_missing_metrics.append("maksuvalmius")
            self.exp_missing_metrics.append("sijoittajan_tunnuslukuja")

        # The tunnuslukuja field is missing on many companies.
        # This means probably that the company is smaller, because Kauppalehti
        # does not provide the most updated tunnuslukuja of the company.
        missing_tunnuslukuja = [2063, 2027, 2042, 2055, 2050, 2074, 2026, 2033,
                                2035, 2040, 2069, 2045, 2034, 2025, 2073, 1953]
        if self.company_id  in missing_tunnuslukuja:
            self.exp_missing_metrics.append("tunnuslukuja")

    def controll_metrics(self):
        # Find failed and missing metrics
        # If a metric is expected to be missing it is not appended in the
        # missing_metrics.
        failed_metrics = []
        exp_missing_metrics = []
        missing_metrics = []

        for key, value in self.metrics.items():
            if value == "FAIL":
                failed_metrics.append(key)
            elif value is None:
                if key in self.exp_missing_metrics:
                    exp_missing_metrics.append(key)
                else:
                    missing_metrics.append(key)
            elif key in self.exp_missing_metrics:
                failed_metrics.append("EXISTS: " + key)

        if failed_metrics:
            self.metrics["failed_metrics"] = failed_metrics
        else:
            self.metrics["failed_metrics"] = None
        if exp_missing_metrics:
            self.metrics["exp_missing_metrics"] = exp_missing_metrics
        else:
            self.metrics["exp_missing_metrics"] = None
        if missing_metrics:
            self.metrics["missing_metrics"] = missing_metrics
        else:
            self.metrics["missing_metrics"] = None

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
        if not v or ( isinstance(v, str) \
                      and ( v.strip() == "" or v.strip() == "-" ) ):
            return None

        if expected_type == int or expected_type == float:
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
            try:
                v = str(v).strip().lower()
                # possible confusing characters in string
                v = v.replace("\"", "").replace("'", "")
                # the scandinavian letters:
                # TODO: Is this needed? Test if no problems.
                v = v.replace("\xe4", "a").replace("\xe5", "a")
                v = v.replace("\xf6", "o")
                # remove noncompatibel characters in unicode (\x80-\xFF):
                # TODO: Could use unicode instead.
                v = re.sub(r'[^\x00-\x7F]+','', v)
            except ValueError:
                raise ScrapeException(exception_str)
        elif expected_type == date:
            v = v.strip()

            if date_pattern_1.match(v): # DD.MM.YYYY
                dd, mm, yyyy = v.split(".")
                if int(dd) > 31 or  int(dd) < 1 \
                or int(mm) > 12 or int(mm) < 1 \
                or int(yyyy) < 1:
                    raise ScrapeException(exception_str)
                v = "{}-{}-{}".format(yyyy, mm, dd) # YYYY-MM-DD

            elif date_pattern_2.match(v): # MM/YY
                mm, yy = v.split("/")
                if int(mm) > 12 or int(mm) < 1 \
                or int(yy) < 1 or int(yy) > 50:
                    raise ScrapeException(exception_str)
                v = "20{}-{}-01".format(yy, mm) # YYYY-MM-DD

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
        self.metrics["company_id"] = self.company_id
        self.metrics["scrape_date"] = date.today().strftime(date_format)

        self.metrics["osingot"] = self.get_osingot()

        self.metrics["company_name"] = self.get_name()
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

        self.define_expected_missing_metrics()
        self.controll_metrics()

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
            if osingot:
                return osingot
            else:
                return None
        except:
            traceback.print_exc()
            return "FAIL"


    def get_name(self):
        try:
            if not self.soup_kurssi:
                self.make_soup_kurssi()

            content_div = self.soup_kurssi.find(id="content")
            name = content_div.find("h1").text
            name = name.lower().replace("oyj","").split("(")[0].strip()
            name = self.pretty_val(name, str)
            if name:
                return name
            else:
                return None
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
            if kurssi:
                return kurssi
            else:
                return None
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
            if kuvaus:
                return kuvaus
            else:
                return None
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
            if perustiedot:
                return perustiedot
            else:
                return None
        except:
            traceback.print_exc()
            return "FAIL"

    def get_tunnuslukuja(self):
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
                #logger.debug("c_id: {}; NO tunnuslukuja".format(self.company_id))
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
            if tunnuslukuja:
                return tunnuslukuja
            else:
                return None
        except:
            traceback.print_exc()
            return "FAIL"


    def get_tulostiedot(self, header, head=None, attempt=1):
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
                #logger.debug("c_id: {}; NO {}".format(self.company_id, header))
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
                if len(head) != row_count - 1:
                    if attempt <= self.max_scrape_retries:
                        if attempt == self.max_scrape_retries:
                            time.sleep(self.wait_before_last_retry)
                        raise ScrapeNetworkException()
                    else:
                        raise ScrapeAgainFailedException()
            # type_row_list[0] is like: "12/16"
            for col in range(1, col_count):
                if type_row_list[0][col]:
                    sub_dict = {}
                    for row in range(1, row_count):
                        if head:
                            sub_dict[head[row - 1]] = type_row_list[row][col]
                        else:
                            sub_dict[type_row_list[row][0]] = type_row_list[row][col]
                    tulostiedot[self.pretty_val(type_row_list[0][col], date)] = sub_dict
            if tulostiedot:
                return tulostiedot
            else:
                return None
        except ScrapeNetworkException:
            logger.debug("Try again: c_id: {}; header: {}; attempt: {}".format(
                self.company_id, header, attempt
            ))
            attempt += 1
            self.make_soup_tulostiedot()
            retval =  self.get_tulostiedot(header, head, attempt)
            if retval != "FAIL":
                logger.debug("Scraping again was successfull for: " + \
                             "c_id: {}; header: {}; attempt: {}".format(
                                 self.company_id, header, attempt
                ))
            return retval
        except ScrapeAgainFailedException:
            logger.debug("Scraping failed: " + \
                "c_id: {}; header: {}; Expected rows: {}; Got: {}".format(
                    self.company_id, header, len(head), row_count - 1
            ))
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
