import requests, logging
from bs4 import BeautifulSoup

import storage

logger = logging.getLogger('root')


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url =               url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url =        url_basic + "osingot/osinkohistoria.jsp?klid={}"            #ID loppuun!
kurssi_url =                url_basic + "porssikurssit/osake/index.jsp?klid={}"         #ID loppuun!
kurssi_tulostiedot_url =    url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"   #ID loppuun!


class Company():
    def __init__(self, company_id, name="Unknown"):
        self.company_id = company_id
        self.name = name
        self.metrics = {}

    def scrape(self):
        url = osingot_yritys_url.format(self.company_id)
        self.osingot = get_osingot(url)

        url = kurssi_url.format(self.company_id)
        self.kurssi = get_kurssi(url)
        self.kuvaus_yrityksesta = get_kuvaus_yrityksesta(url)
        self.perustiedot_dict = get_perustiedot(url)
        self.tunnuslukuja_dict = get_tunnuslukuja(url)

        url = kurssi_tulostiedot_url.format(self.company_id)
        self.toiminnan_laajuus_mat = get_kurssi_tulostiedot(url, "Toiminnan laajuus")
        self.kannattavuus_mat = get_kurssi_tulostiedot(url, "Kannattavuus")
        self.vakavaraisuus_mat = get_kurssi_tulostiedot(url, "Vakavaraisuus")
        self.maksuvalmius_mat = get_kurssi_tulostiedot(url, "Maksuvalmius")
        self.sijoittajan_tunnuslukuja_mat = get_kurssi_tulostiedot(url, "Sijoittajan tunnuslukuja")

        self.set_metrics()
        self.set_representations()

    @staticmethod
    def load_from_file(filename):
        stored_scrape, scrape_type = storage.get_stored_company_list(filename)
        # TODO: unpacking of stored_scrape, depending on the scrape_type
        company_list = []
        return company_list

    def set_metrics(self):
        # TODO: get the metrics from scraped data into better format
        pass

    @staticmethod
    def list_to_str(company_list, name, tsv=False):
        if company_list[0]:
            if tsv:
                string = "\n# {}".format(name)
            else:
                string = "\n{}".format(name)
            for i in range(1, len(company_list)):
                string = string + "\n"
                for j in company_list[i]:
                    # one tab is 8 spaces/characters
                    if tsv:
                        string = string + "{}\t".format(j)
                    else:
                        string = string + "\t%-15.15s" % str(j)
                if tsv:
                    string.rstrip()
        else:
            string = "\n{}: Empty".format(name)
        return string

    @staticmethod
    def dict_to_str(company_dict, name, tsv=False):
        if company_dict[0]:
            if tsv:
                string = "\n# {}".format(name)
            else:
                string = "\n{}".format(name)
            for i in company_dict:
                # one tab is 8 spaces/characters
                if i != 0:
                    if tsv:
                        string = string + "\n{}\t{}".format(i, str(company_dict[i]))
                    else:
                        string = string + "\n\t%-31.31s:%s" % (i, str(company_dict[i]))
        else:
            string = "\n{}: Empty".format(name)
        return string

    def set_representations(self):
        """
        print(self.company_id)
        print(self.name)
        print(self.kurssi)
        print(self.kuvaus_yrityksesta)
        print(self.osingot)
        print(self.perustiedot_dict)
        print(self.tunnuslukuja_dict)
        print(self.toiminnan_laajuus_mat)
        print(self.kannattavuus_mat)
        print(self.vakavaraisuus_mat)
        print(self.maksuvalmius_mat)
        print(self.sijoittajan_tunnuslukuja_mat)
        """

        self.str_raw = "company_id:\t{}\nName:\t{}".format(self.company_id, self.name) +\
            "\nKurssi:\t{}\nKuvaus:\t{}".format(self.kurssi, self.kuvaus_yrityksesta) +\
            self.list_to_str(self.osingot,                        "osingot") +\
            self.dict_to_str(self.perustiedot_dict,               "perustiedot") +\
            self.dict_to_str(self.tunnuslukuja_dict,              "tunnuslukuja") +\
            self.list_to_str(self.toiminnan_laajuus_mat,          "toiminnan_laajuus") +\
            self.list_to_str(self.kannattavuus_mat,               "kannattavuus") +\
            self.list_to_str(self.vakavaraisuus_mat,              "vakavaraisuus") +\
            self.list_to_str(self.maksuvalmius_mat,               "maksuvalmius") +\
            self.list_to_str(self.sijoittajan_tunnuslukuja_mat,   "sijoittajan_tunnuslukuja")

        self.tsv_raw = "\n## company_id\t{}\nName\t{}".format(self.company_id, self.name) +\
            "\nKurssi\t{}\nKuvaus\t{}".format(self.kurssi, self.kuvaus_yrityksesta) +\
            self.list_to_str(self.osingot,                        "osingot",                    True) +\
            self.dict_to_str(self.perustiedot_dict,               "perustiedot",                True) +\
            self.dict_to_str(self.tunnuslukuja_dict,              "tunnuslukuja",               True) +\
            self.list_to_str(self.toiminnan_laajuus_mat,          "toiminnan_laajuus",          True) +\
            self.list_to_str(self.kannattavuus_mat,               "kannattavuus",               True) +\
            self.list_to_str(self.vakavaraisuus_mat,              "vakavaraisuus",              True) +\
            self.list_to_str(self.maksuvalmius_mat,               "maksuvalmius",               True) +\
            self.list_to_str(self.sijoittajan_tunnuslukuja_mat,   "sijoittajan_tunnuslukuja",   True)

        # TODO: str metrics
        self.str_metrics = "Under work"

        # TODO: tsv metrics
        self.tsv_metrics = "Under work"

    def __repr__(self):
        return self.str_metrics


# TODO: Is this needed
class Scrape():
    def __init__(self):
        pass

    def __repr__(self):
        return __dict__

    def set_from_scrape(self, DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys):
        self.DICT_YRITYKSEN_TIEDOT = DICT_YRITYKSEN_TIEDOT
        self.scraped_IDs = scraped_IDs
        self.DICT_yritys=DICT_yritys
    """
    def set_from_csv_file(self, filename):
        DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys = storage.DICT_YRITYKSEN_TIEDOT_csv_file_READ(filename)

        self.DICT_YRITYKSEN_TIEDOT = DICT_YRITYKSEN_TIEDOT
        self.scraped_IDs = scraped_IDs
        self.DICT_yritys = DICT_yritys

    def save_to_csv_file(self):
        storage.DICT_YRITYKSEN_TIEDOT_csv_file_WRITE(self.DICT_YRITYKSEN_TIEDOT, self.scraped_IDs, self.DICT_yritys)
    """

class Yritys():
    def __init__(self, ID, Tiedot_olio):
        self.company_id=ID
        self.Tiedot=Tiedot_olio
        self.nimi=Tiedot_olio.DICT_yritys[ID]
        
        self.set_yritysksen_tiedot()
    
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
    
    def set_yritysksen_tiedot(self):
        #POIMI TIEDOT
        self.set_osinko_tiedot()
        self.set_kurssi_tiedot()
        self.set_kurssi_tulostiedot()
        
        
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
    
    def set_osinko_tiedot(self):
        #osinkoa on tasaisesti jaettu viiden vuoden ajan (osinkotuotto >0% joka vuosi)
        self.on_jaettu_viisi_vuotta_osinkoa=None
        self.viime_osinko=None
        c=0
        for i in self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][0]:
            if c>1:
                #print(i, i[3], i[5])
                try:
                    if not (i[5]>0):
                        self.on_jaettu_viisi_vuotta_osinkoa=False
                        break
                except:
                    logger.debug("osinko")
                    self.on_jaettu_viisi_vuotta_osinkoa=False
                    break
            if c==2:
                self.viime_osinko=i[3]
            if c==6:
                if i[0]!=2012:
                    logger.debug("osinko outoa")
                    self.on_jaettu_viisi_vuotta_osinkoa=False
                    break
                self.on_jaettu_viisi_vuotta_osinkoa=True
                break
            c+=1
        
        if self.on_jaettu_viisi_vuotta_osinkoa==False:
            self.viime_osinko=False
    
    def set_kurssi_tiedot(self):
        #nykyinen kurssi
        val=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][1]
        if type(val)==float:
            self.nykyinen_kurssi=val
        else:
            logger.debug("nykyinen_kurssi")
            self.nykyinen_kurssi=False
        
        #Kuvaus
        self.kuvaus=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][2]
        
        #Toimiala, Toimialaluokka, Kappaletta osakkeita
        perus_dict=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][3]
        if perus_dict[0]:
            self.toimiala=perus_dict["Toimiala"]
            self.toimialaluokka=perus_dict["Toimialaluokka"]
            self.kpl_osakkeita=perus_dict["Osakkeet (KPL)"]
        else:
            logger.debug("toimiala TAI toimialaluokka")
            self.toimiala=False
            self.toimialaluokka=False
            self.kpl_osakkeita=False
    
    def poimi_arvo_tuolostiedoista(self, matrix, header, rivi, sarake):
        if matrix[0]:
            vuodet=['VUOSI', '12/15', '12/14', '12/13', '12/12', '12/11']
            vuosi=matrix[1][sarake]
            head=matrix[rivi][0]
            if head==header and vuosi==vuodet[sarake]:
                val=matrix[rivi][sarake]
                #print(val)
                if type(val)==float:
                    return val
                else:
                    logger.debug(header)
                    return False
        logger.debug(header)
        return False
    
    def set_kurssi_tulostiedot(self):
        ##TOIMINNAN LAAJUUS
        """
        toim_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][5]
        if toim_mat[0]:
            pass
        else:
            logger.debug("DICT_toiminnan_laajuus_mat PUUTTUU TAI ON VIALLINEN")
        """
        
        ##KANNATTAVUUS
        kann_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][6]
        if kann_mat[0]:
            #ROE (Oman paaoman tuotto, %)
            self.ROE=self.poimi_arvo_tuolostiedoista(kann_mat, "Oman paaoman tuotto, %", 7, 1)
            
            #Nettotulokset
            self.nettotulokset=[]
            for i in range(1,6):
                val=self.poimi_arvo_tuolostiedoista(kann_mat, "Nettotulos", 4, i)
                self.nettotulokset.append(val)
        else:
            logger.debug("DICT_kannattavuus_mat PUUTTUU TAI ON VIALLINEN")
            self.ROE=False
            self.nettotulokset=False
        
        ##VAKAVARAISUUS
        vaka_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][7]
        if vaka_mat[0]:
            #Omavaraisuusaste, %
            self.omavaraisuusaste=self.poimi_arvo_tuolostiedoista(vaka_mat, "Omavaraisuusaste, %", 2, 1)
            
            #Gearing (Nettovelkaantumisaste, %)
            self.gearing=self.poimi_arvo_tuolostiedoista(vaka_mat, 'Nettovelkaantumisaste, %', 3, 1)
        else:
            logger.debug("DICT_vakavaraisuus_mat PUUTTUU TAI ON VIALLINEN")
            self.omavaraisuusaste=False
            self.gearing=False
        
        ##MAKSUVALMIUS
        """
        maksu_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][8]
        if maksu_mat[0]:
            pass
        else:
            logger.debug("DICT_maksuvalmius_mat PUUTTUU TAI ON VIALLINEN")
        """
        
        ##SIJOITTAJAN TUNNUSLUKUJA
        sijo_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.company_id][9]
        if sijo_mat[0]:
            #P/B-luku
            self.PB_luku=self.poimi_arvo_tuolostiedoista(sijo_mat, 'P/B-luku', 6, 1)
            
            #P/E-luku
            self.PE_luku=self.poimi_arvo_tuolostiedoista(sijo_mat, 'P/E-luku', 8, 1)
            
            #Tulos (E), (oikea tulos vahennysten jalkeen)
            self.E_luku=self.poimi_arvo_tuolostiedoista(sijo_mat, 'Tulos (E)', 5, 1)
            
            #Markkina-arvo (P)
            self.P_luku=self.poimi_arvo_tuolostiedoista(sijo_mat, 'Markkina-arvo (P)', 2, 1)
        else:
            logger.debug("DICT_sijoittajan_tunnuslukuja_mat PUUTTUU TAI ON VIALLINEN")
            self.PB_luku=False
            self.PE_luku=False
            self.E_luku=False
            self.P_luku=False


def get_raw_soup(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

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
        
        OYV=[]  #Osingot yritykselle yhdella rivilla        Vuosi, Irtoaminen, Oikaistu euroina, Maara, Valuutta, Tuotto-%, Lisatieto
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

def get_kuvaus_yrityksesta(url):
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
