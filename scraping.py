import requests, logging
from bs4 import BeautifulSoup
from datetime import datetime

import storage

logger = logging.getLogger('root')


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"


class Company():
    def __init__(self, company_id=None, name="Unknown", metrics=None):
        self.company_id = company_id
        self.company_name = name
        self.scrape_date = None # datetime.date Object

        if metrics:
            self.metrics = metrics
            self.company_id = self.metrics["company_id"]
            self.company_name = self.metrics["company_name"]
            self.scrape_date = datetime.strptime(self.metrics["scrape_date"], "%y-%m-%d")

            self.after_basic_metrics_is_set()
        else:
            self.metrics = {}

        assert self.company_id, "Company has no id"

    def __repr__(self):
        return "Company({}, {})".format(self.company_id, self.company_name)

    @staticmethod
    def load_from_file(filename):
        company_list = storage.get_stored_companies(filename)
        logger.debug("Loaded {} companies from {}".format(len(company_list), filename))
        return company_list

    def scrape(self):
        url_os = osingot_yritys_url.format(self.company_id)
        url_ku = kurssi_url.format(self.company_id)
        url_ku_tu = kurssi_tulostiedot_url.format(self.company_id)

        self.metrics["company_id"] = self.company_id
        self.metrics["company_name"] = self.company_name
        self.scrape_date = datetime.now().date() # YY-MM-DD
        self.metrics["scrape_date"] = self.scrape_date.strftime("%y-%m-%d")

        self.metrics["kurssi"] = get_kurssi(url_ku)
        self.metrics["kuvaus"] = get_kuvaus(url_ku)

        self.metrics["osingot"] = self.list_to_pretty_dict(get_osingot(url_os))

        self.metrics["perustiedot"] = self.dict_to_pretty_dict(get_perustiedot(url_ku))
        self.metrics["tunnuslukuja"] = self.dict_to_pretty_dict(get_tunnuslukuja(url_ku))

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

        self.after_basic_metrics_is_set()

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

    def after_basic_metrics_is_set(self):
        if not "calculations" in self.metrics:
            self.calculate_metrics()
        self.set_representations()

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

    def set_representations(self):
        assert self.metrics
        self.tsv_metrics = "\n{}".format(self.metrics)
        self.str_metrics = self.add_dict_to_str(self.metrics)
        self.str_metrics_simple = self.add_dict_to_str(self.metrics, simple=True)

    # TODO: UNDER IS OLD FUNCTIONS: go troghe

    def calculate_metrics(self):
        assert self.metrics
        self.metrics["calculations"] = {}
        self.calculate_osinko()
        self.collect_metrics()
        
        """
        was nothing (maby was not yet implemented...)
            toiminnan laajuus
            maksuvalmius
        
        perustiedot
            Toimiala
            Toimialaluokka
            Kappaletta osakkeita
        kannattavuus
            ROE: Oman paaoman tuotto, %
            nettotulokset: Nettotulos
        vakavaraisuus
            omavaraisuusaste: Omavaraisuusaste, %
            gearing: Nettovelkaantumisaste, %
        sijoittajan_tunnuslukuja
            PB_luku
            PE_luku
            E_luku: Tulos (E)
            P_luku: Markkina-arvo (P)
        """
        
        """
        #POIMI TIEDOT
        
        
        #LASKE NYKYISIA LUKUJA
        if self.viime_osinko and self.nykyinen_kurssi:
            self.nykyinen_osinkotuotto_PROCENT = round( 100* self.viime_osinko / self.nykyinen_kurssi, 2)
        else:
            self.nykyinen_osinkotuotto_PROCENT=False
        
        
        if self.kpl_osakkeita and self.nykyinen_kurssi:
            self.nykyinen_P_luku = round( self.kpl_osakkeita * self.nykyinen_kurssi /1000000, 4)
        else:
            self.nykyinen_P_luku=False
        
        if self.P_luku and self.nykyinen_P_luku:
            self.P_muutos_kerroin = round( self.nykyinen_P_luku / self.P_luku, 4)
        else:
            self.P_muutos_kerroin=False
        
        if self.P_muutos_kerroin and self.PB_luku:
            self.nykyinen_PB_luku = round( self.P_muutos_kerroin * self.PB_luku, 2)
        else:
            self.nykyinen_PB_luku=False
        
        if self.P_muutos_kerroin and self.PE_luku:
            self.nykyinen_PE_luku = round( self.P_muutos_kerroin * self.PE_luku, 2)
        else:
            self.nykyinen_PE_luku=False
        
        
        
        self.tiedot_print()
        self.kiinnostavat_tunnusluvut_print()
        """
        
        print("\n" + "+"*10 + "\tcalculations:" + self.add_dict_to_str(self.metrics["calculations"]))

    def addCalc(self, key, value):
        assert not str(key) in self.metrics["calculations"]
        self.metrics["calculations"][str(key)] = value

    def calculate_osinko(self):
        # steady osinko: osinkotuotto > 0% for five years
        current_year = int(datetime.now().strftime("%Y")) # YYYY
        osinko_tuotto_prosentti = {}
        osinko_euro = {}
        for year in range(current_year-4, current_year+1):
            osinko_tuotto_prosentti[str(year)] = 0
            osinko_euro[str(year)] = 0

        for top_key in self.metrics["osingot"]:
            osinko_dict = self.metrics["osingot"][top_key]
            osinko_year = str(osinko_dict["vuosi"])
            if osinko_year in osinko_tuotto_prosentti:
                osinko_tuotto_prosentti[osinko_year] += osinko_dict["tuotto-%"]
                osinko_euro[osinko_year] += osinko_dict["oikaistu euroina"]

        steady_osinko_bool = 1 # 1: True, 0: False
        for year in osinko_tuotto_prosentti:
            if osinko_tuotto_prosentti[year] <= 0:
                steady_osinko_bool = 0
                break

        self.addCalc("osinko_tuotto_prosentti", osinko_tuotto_prosentti)
        self.addCalc("osinko_euro", osinko_euro)
        self.addCalc("steady_osinko_bool", steady_osinko_bool)

    def set_taloustiedot_current_key(self):
        self.tt_current_key = None # "12/16", used for dictionaries scraped from the tulostiedot-page
        current_year = int(datetime.now().strftime("%y")) # YY
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
            logger.error("Problem with keys: {}".format(str(all_keys)))
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
        self.addCalc("osakkeet_kpl", self.metrics["perustiedot"]["osakkeet (kpl)"])

        self.addCalc("ROE", self.metrics["kannattavuus"][self.tt_current_key]["oman paaoman tuotto, %"])
        self.addCalc("nettotulos", self.metrics["kannattavuus"][self.tt_current_key]["nettotulos"])

        self.addCalc("omavaraisuusaste", self.metrics["vakavaraisuus"][self.tt_current_key]["omavaraisuusaste, %"])
        self.addCalc("gearing", self.metrics["vakavaraisuus"][self.tt_current_key]["nettovelkaantumisaste, %"])

        self.addCalc("PB", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["p/b-luku"])
        self.addCalc("PE", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["p/e-luku"])
        self.addCalc("E", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["tulos (e)"])
        self.addCalc("P", self.metrics["sijoittajan_tunnuslukuja"][self.tt_current_key]["markkina-arvo (p)"])


    def tiedot_print(self):
        #print(": ", self.)
        
        print("\n\tPOIMITUT ARVOT:")
        
        print("nykyinen_kurssi: ", self.nykyinen_kurssi)
        print("viime_osinko (EUR): ", self.viime_osinko)
        print("on_jaettu_viisi_vuotta_osinkoa: ", self.on_jaettu_viisi_vuotta_osinkoa)
        
        print("\nomavaraisuusaste: ", self.omavaraisuusaste)
        print("gearing: ", self.gearing)
        print("kpl_osakkeita: ", self.kpl_osakkeita)
        print("nettotulokset: ", self.nettotulokset)
        
        print("\nROE: ", self.ROE)
        print("P_luku: ", self.P_luku)
        print("E_luku: ", self.E_luku)
        print("PB_luku: ", self.PB_luku)
        print("PE_luku: ", self.PE_luku)
        
        print("\nToimiala: ", self.toimiala)
        print("Toimialaluokka: ", self.toimialaluokka)
        print("Kuvaus: ", self.kuvaus)
        
        
        print("\n\tLASKETTUA:")
        
        print("nykyinen_osinkotuotto_PROCENT: ", self.nykyinen_osinkotuotto_PROCENT)
        print("nykyinen_P_luku: ", self.nykyinen_P_luku)
        print("P_muutos_kerroin: ", self.P_muutos_kerroin)
        print("nykyinen_PB_luku: ", self.nykyinen_PB_luku)
        print("nykyinen_PE_luku: ", self.nykyinen_PE_luku)

    def kiinnostavat_tunnusluvut_print(self):
        print("\n\tKIINNOSTAVAT TUNNUSLUVUT:")
        print("Nimi\t\tLuku\tVanha\n\tKarsinta:")
        print("Gearing\t\t{}".format(self.gearing))
        print("Omavaraisuusas.\t{}".format(self.omavaraisuusaste))
        print("ROE\t\t{}".format(self.ROE))
        print("Osinko jaettu\t{}".format(self.on_jaettu_viisi_vuotta_osinkoa))
        vuodet=['VUOSI', '12/15', '12/14', '12/13', '12/12', '12/11']
        c=1
        for i in self.nettotulokset:
            print("N.tulos ({})\t{}".format(vuodet[c], i))
            c+=1
        print("\tJarjestys:")
        print("PB_luku\t\t{}\t{}".format(self.nykyinen_PB_luku, self.PB_luku))
        print("PE_luku\t\t{}\t{}".format(self.nykyinen_PE_luku, self.PE_luku))
        print("Osinkot. (%)\t{}".format(self.nykyinen_osinkotuotto_PROCENT))
        print("ROE\t\t{}".format(self.ROE))



def get_raw_soup(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

# TODO: Go trough old functions here under and write tests for them

def fix_str(string):
    # deals with scandinavian characters
    return string.replace("\xe4", "a").replace("\xe5", "a").replace("\xf6", "o")

def fix_str_noncompatible_chars_in_unicode(string):
    return string.replace("\x9a","?").replace("\x96","?").replace("\x92","?")

def scrape_company_names():
    soup = get_raw_soup(osingot_url)

    form_tags = soup.find_all('form')
    option_tags = form_tags[2].find_all('option')

    yritys_dict = {}
    for i in option_tags:
        name = i.string
        ID = i.attrs['value']
        try:
            ID = int(ID)
            yritys_dict[ID] = name
        except:
            pass
    return yritys_dict

def get_osingot(url):
    soup = get_raw_soup(url)
    yrityksen_osingot=["NOT REDY"]
    
    table_tags=soup.find_all('table')
    table_row_tags=table_tags[5].find_all('tr')
    c=0
    for i in table_row_tags:
        columns=i.find_all('td')
        
        OYV=[]
        """Osingot yritykselle yhdella rivilla:
            Vuosi, Irtoaminen, Oikaistu euroina,
            Maara, Valuutta, Tuotto-%, Lisatieto"""
        if c==0:
            OYV.append("Vuosi")
            OYV.append("Irtoaminen")
            OYV.append("Oikaistu euroina")
            OYV.append("Maara")
            OYV.append("Valuutta")
            OYV.append("Tuotto-%")
            OYV.append("Lisatieto")
        else:
            for i in range(7):
                val=columns[i].string
                if i==0:
                    try:
                        val=int(val)
                    except:
                        logger.debug("int('{}')".format(val))
                elif i==2 or i==3 or i==5:
                    try:
                        val=float(val)
                    except:
                        logger.debug("int('{}')".format(val))
                OYV.append(val)
            
        yrityksen_osingot.append(OYV)
        c+=1
    yrityksen_osingot[0]=True
    return yrityksen_osingot

def get_kurssi(url):
    soup = get_raw_soup(url)
    try:
        table_tags=soup.find_all('table')
        
        kurssi=table_tags[5].find('span').text
        try:
            kurssi=float(kurssi)
        except:
            logger.debug("float(kurssi)")
        
    except:
        logger.debug("kurssi")
        kurssi="FAIL"
    return kurssi

def get_kuvaus(url):
    soup = get_raw_soup(url)
    try:
        class_padding_tags=soup.find_all(class_="paddings")
        
        for tag in class_padding_tags:
            if tag.parent.h3.text=="Yrityksen perustiedot":
                kuvaus_yrityksesta = tag.p.text.strip().replace("\n"," ").replace("\r"," ")
                #kuvaus_yrityksesta = fix_str(kuvaus_yrityksesta)
                kuvaus_yrityksesta = fix_str_noncompatible_chars_in_unicode(kuvaus_yrityksesta)
                return kuvaus_yrityksesta
        
        logger.debug("kuvaus_yrityksesta EI LOYTYNYT")
        kuvaus_yrityksesta="FAIL"
    except:
        logger.debug("kuvaus_yrityksesta")
        kuvaus_yrityksesta="FAIL"
    return kuvaus_yrityksesta

def get_osakkeen_perustiedot_table_TAG(url):
    soup = get_raw_soup(url)
    try:
        class_is_TSBD=soup.find_all(class_="table_stock_basic_details")
        
        for tag in class_is_TSBD:
            try:
                if tag.parent.parent.h3.text.strip() == "Osakkeen perustiedot":
                    return tag
            except:
                pass
        logger.debug("osakkeen_perustiedot_table_TAG EI LOYTYNYT")
    except:
        logger.debug("osakkeen_perustiedot_table_TAG")
    return -1

def get_perustiedot(url):
    perustiedot_dict={}
    try:
        TAG=get_osakkeen_perustiedot_table_TAG(url)
        
        if TAG == -1:
            perustiedot_dict[0]=False
            return perustiedot_dict
        
        tr_tags=TAG.find_all('tr')
        c=0
        for i in tr_tags:
            td_tags=i.find_all('td')
            
            if c==0:
                key=td_tags[0].text.replace(":","")
                val=td_tags[1].text
                perustiedot_dict[fix_str(key)]=val
                
                strs=td_tags[2].text.split("\n")
                [key, val]=strs[1].split(":")
                perustiedot_dict[fix_str(key)]=val
                
                [key, val]=strs[2].split(":")
                perustiedot_dict[fix_str(key)]=val
                c+=1
            else:
                key=td_tags[0].text.strip().replace(":","")
                val=td_tags[1].text.strip()
                
                if key=="Osakkeet":
                    val= val.replace("kpl","").replace("\xa0", "")
                    key="{} (KPL)".format(key)
                    try:
                        val=int(val)
                    except:
                        logger.debug("Osakkeet (KPL)")
                
                perustiedot_dict[fix_str(key)]=val
        
        perustiedot_dict[0]=True
    except:
        logger.debug("perustiedot_dict")
        perustiedot_dict[0]=False
    return perustiedot_dict

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

def get_tunnuslukuja(url):
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
            
            tunnuslukuja_dict[fix_str(key)]=val
            c+=1
        
        tunnuslukuja_dict[0]=True
    except:
        logger.debug("tunnuslukuja_dict")
        tunnuslukuja_dict[0]=False
    return tunnuslukuja_dict



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
                    val=fix_str(j.text.strip())
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
