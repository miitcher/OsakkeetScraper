import requests, logging
from bs4 import BeautifulSoup

import storage
from console_display import ERROR_LOG


class Tiedot_luokka():
    def __init__(self):
        pass
    
    def set_from_scrape(self, DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys):
        self.DICT_YRITYKSEN_TIEDOT = DICT_YRITYKSEN_TIEDOT
        self.scraped_IDs = scraped_IDs
        self.DICT_yritys=DICT_yritys
    
    def set_from_csv_file(self, filename):
        DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys = storage.DICT_YRITYKSEN_TIEDOT_csv_file_READ(filename)
        
        self.DICT_YRITYKSEN_TIEDOT = DICT_YRITYKSEN_TIEDOT
        self.scraped_IDs = scraped_IDs
        self.DICT_yritys = DICT_yritys
    
    def save_to_csv_file(self):
        storage.DICT_YRITYKSEN_TIEDOT_csv_file_WRITE(self.DICT_YRITYKSEN_TIEDOT, self.scraped_IDs, self.DICT_yritys)


class Yritys():
    def __init__(self, ID, Tiedot_olio):
        self.ID=ID
        self.Tiedot=Tiedot_olio
        self.nimi=Tiedot_olio.DICT_yritys[ID]
        
        self.set_yritysksen_tiedot()
    
    def ERROR(self, f, description):
        ERROR_LOG(self.ID, f, "Yritys-OLIO: {}".format(description))
    
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
        f="set_osinko_tiedot"
        #osinkoa on tasaisesti jaettu viiden vuoden ajan (osinkotuotto >0% joka vuosi)
        self.on_jaettu_viisi_vuotta_osinkoa=None
        self.viime_osinko=None
        c=0
        for i in self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][0]:
            if c>1:
                #print(i, i[3], i[5])
                try:
                    if not (i[5]>0):
                        self.on_jaettu_viisi_vuotta_osinkoa=False
                        break
                except:
                    self.ERROR(f, "osinko")
                    self.on_jaettu_viisi_vuotta_osinkoa=False
                    break
            if c==2:
                self.viime_osinko=i[3]
            if c==6:
                if i[0]!=2012:
                    self.ERROR(f, "osinko outoa")
                    self.on_jaettu_viisi_vuotta_osinkoa=False
                    break
                self.on_jaettu_viisi_vuotta_osinkoa=True
                break
            c+=1
        
        if self.on_jaettu_viisi_vuotta_osinkoa==False:
            self.viime_osinko=False
    
    def set_kurssi_tiedot(self):
        f="set_kurssi_tiedot"
        #nykyinen kurssi
        val=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][1]
        if type(val)==float:
            self.nykyinen_kurssi=val
        else:
            self.ERROR(f, "nykyinen_kurssi")
            self.nykyinen_kurssi=False
        
        #Kuvaus
        self.kuvaus=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][2]
        
        #Toimiala, Toimialaluokka, Kappaletta osakkeita
        perus_dict=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][3]
        if perus_dict[0]:
            self.toimiala=perus_dict["Toimiala"]
            self.toimialaluokka=perus_dict["Toimialaluokka"]
            self.kpl_osakkeita=perus_dict["Osakkeet (KPL)"]
        else:
            self.ERROR(f, "toimiala TAI toimialaluokka")
            self.toimiala=False
            self.toimialaluokka=False
            self.kpl_osakkeita=False
    
    def poimi_arvo_tuolostiedoista(self, matrix, header, rivi, sarake):
        f="poimi_arvo_tuolostiedoista (tulostiedot)"
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
                    self.ERROR(f, header)
                    return False
        self.ERROR(f, header)
        return False
    
    def set_kurssi_tulostiedot(self):
        f="set_kurssi_tulostiedot"
        ##TOIMINNAN LAAJUUS
        """
        toim_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][5]
        if toim_mat[0]:
            pass
        else:
            self.ERROR(f, "DICT_toiminnan_laajuus_mat PUUTTUU TAI ON VIALLINEN")
        """
        
        ##KANNATTAVUUS
        kann_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][6]
        if kann_mat[0]:
            #ROE (Oman paaoman tuotto, %)
            self.ROE=self.poimi_arvo_tuolostiedoista(kann_mat, "Oman paaoman tuotto, %", 7, 1)
            
            #Nettotulokset
            self.nettotulokset=[]
            for i in range(1,6):
                val=self.poimi_arvo_tuolostiedoista(kann_mat, "Nettotulos", 4, i)
                self.nettotulokset.append(val)
        else:
            self.ERROR(f, "DICT_kannattavuus_mat PUUTTUU TAI ON VIALLINEN")
            self.ROE=False
            self.nettotulokset=False
        
        ##VAKAVARAISUUS
        vaka_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][7]
        if vaka_mat[0]:
            #Omavaraisuusaste, %
            self.omavaraisuusaste=self.poimi_arvo_tuolostiedoista(vaka_mat, "Omavaraisuusaste, %", 2, 1)
            
            #Gearing (Nettovelkaantumisaste, %)
            self.gearing=self.poimi_arvo_tuolostiedoista(vaka_mat, 'Nettovelkaantumisaste, %', 3, 1)
        else:
            self.ERROR(f, "DICT_vakavaraisuus_mat PUUTTUU TAI ON VIALLINEN")
            self.omavaraisuusaste=False
            self.gearing=False
        
        ##MAKSUVALMIUS
        """
        maksu_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][8]
        if maksu_mat[0]:
            pass
        else:
            self.ERROR(f, "DICT_maksuvalmius_mat PUUTTUU TAI ON VIALLINEN")
        """
        
        ##SIJOITTAJAN TUNNUSLUKUJA
        sijo_mat=self.Tiedot.DICT_YRITYKSEN_TIEDOT[self.ID][9]
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
            self.ERROR(f, "DICT_sijoittajan_tunnuslukuja_mat PUUTTUU TAI ON VIALLINEN")
            self.PB_luku=False
            self.PE_luku=False
            self.E_luku=False
            self.P_luku=False


def get_raw_soup(link):
    r=requests.get(link)
    soup=BeautifulSoup(r.text, "html.parser")
    return soup

def get_yritys_dict(soup):
    form_tags=soup.find_all('form')
    option_tags=form_tags[2].find_all('option')
    
    yritys_dict={}
    for i in option_tags:
        name= i.string
        ID= i.attrs['value']
        try:
            ID=int(ID)
            yritys_dict[ID]=name
        except:
            pass
    return yritys_dict

def get_yrityksen_osingot(soup):
    f="get_yrityksen_osingot"
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
                        ERROR_LOG(0, f, "int('{}')".format(val), True)
                elif i==2 or i==3 or i==5:
                    try:
                        val=float(val)
                    except:
                        ERROR_LOG(0, f, "int('{}')".format(val), True)
                OYV.append(val)
            
        yrityksen_osingot.append(OYV)
        c+=1
    yrityksen_osingot[0]=True
    return yrityksen_osingot

def get_kurssi(soup, ID):
    f="get_kurssi"
    try:
        table_tags=soup.find_all('table')
        
        kurssi=table_tags[5].find('span').text
        try:
            kurssi=float(kurssi)
        except:
            ERROR_LOG(ID, f, "float(kurssi)", True)
        
    except:
        ERROR_LOG(ID, f, "kurssi")
        kurssi="FAIL"
    return kurssi

def get_kuvaus_yrityksesta(soup, ID):
    f="get_kuvaus_yrityksesta"
    try:
        class_padding_tags=soup.find_all(class_="paddings")
        
        for tag in class_padding_tags:
            if tag.parent.h3.text=="Yrityksen perustiedot":
                kuvaus_yrityksesta = tag.p.text.strip().replace("\n"," ").replace("\r"," ")
                #kuvaus_yrityksesta = fix_str(kuvaus_yrityksesta)
                kuvaus_yrityksesta = fix_str_noncompatible_chars_in_unicode(kuvaus_yrityksesta)
                return kuvaus_yrityksesta
        
        ERROR_LOG(ID, f, "kuvaus_yrityksesta EI LOYTYNYT", True)
        kuvaus_yrityksesta="FAIL"
    except:
        ERROR_LOG(ID, f, "kuvaus_yrityksesta")
        kuvaus_yrityksesta="FAIL"
    return kuvaus_yrityksesta

def get_osakkeen_perustiedot_table_TAG(soup, ID):
    f="get_osakkeen_perustiedot_table_TAG"
    try:
        class_is_TSBD=soup.find_all(class_="table_stock_basic_details")
        
        for tag in class_is_TSBD:
            try:
                if tag.parent.parent.h3.text.strip() == "Osakkeen perustiedot":
                    return tag
            except:
                pass
        ERROR_LOG(ID, f, "osakkeen_perustiedot_table_TAG EI LOYTYNYT")
    except:
        ERROR_LOG(ID, f, "osakkeen_perustiedot_table_TAG")
    return -1

def get_perustiedot_dict(soup, ID):
    f="get_perustiedot_dict"
    perustiedot_dict={}
    try:
        TAG=get_osakkeen_perustiedot_table_TAG(soup, ID)
        
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
                        ERROR_LOG(ID, f, "Osakkeet (KPL)")
                
                perustiedot_dict[fix_str(key)]=val
        
        perustiedot_dict[0]=True
    except:
        ERROR_LOG(ID, f, "perustiedot_dict")
        perustiedot_dict[0]=False
    return perustiedot_dict

def get_tunnuslukuja_table_TAG(soup, ID):
    f="get_tunnuslukuja_table_TAG"
    try:
        table_tags=soup.find_all('table')
        
        for tag in table_tags:
            try:
                if tag.parent.p.text.strip() == "Tunnuslukuja":
                    return tag
            except:
                pass
        ERROR_LOG(ID, f, "tunnuslukuja_table_TAG EI LOYTYNYT")
    except:
        ERROR_LOG(ID, f, "tunnuslukuja_table_TAG")
    return -1

def get_tunnuslukuja_dict(soup, ID):
    f="get_tunnuslukuja_dict"
    tunnuslukuja_dict={}
    try:
        TAG=get_tunnuslukuja_table_TAG(soup, ID)
        
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
                    description="float({})".format(key)
                    ERROR_LOG(ID, f, description, True)
            elif c==5:
                try:
                    parts=val.split()
                    val=float(parts[0])
                    k=parts[1].split(".")
                    key=key + " ({}. EUR)".format(k[0])
                except:
                    description="float({})".format(key)
                    ERROR_LOG(ID, f, description, True)
            else:
                try:
                    parts=val.split()
                    val=float(parts[0])
                    key=key + " (EUR)"
                except:
                    description="float({})".format(key)
                    ERROR_LOG(ID, f, description, True)
            
            tunnuslukuja_dict[fix_str(key)]=val
            c+=1
        
        tunnuslukuja_dict[0]=True
    except:
        ERROR_LOG(ID, f, "tunnuslukuja_dict")
        tunnuslukuja_dict[0]=False
    return tunnuslukuja_dict



def get_KURSSI_TULOSTIEDOT_table_TAG(soup, ID, otsikko):
    f="get_KURSSI_TULOSTIEDOT_table_TAG"
    try:
        table_tags=soup.find_all(class_="table_stockexchange")
        
        for tag in table_tags:
            try:
                if tag.parent.h3.text.strip() == otsikko:
                    return tag
            except:
                pass
        ERROR_LOG(ID, f, "Otsikko='{}' TAG EI LOYTYNYT".format(otsikko))
    except:
        ERROR_LOG(ID, f, "Otsikko='{}'".format(otsikko))
    return -1

def get_KURSSI_TULOSTIEDOT_mat(soup, ID, otsikko):
    f="get_KURSSI_TULOSTIEDOT_mat"
    matrix=["NOT REDY"]
    try:
        TAG = get_KURSSI_TULOSTIEDOT_table_TAG(soup, ID, otsikko)
        
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
                        ERROR_LOG(ID, f, "Otsikko='{}', float('{}')".format(otsikko, val), True)
                    rivi.append(val)
            
            matrix.append(rivi)
        
        matrix[0]=True
    except:
        ERROR_LOG(ID, f, "Otsikko='{}'".format(otsikko))
        matrix[0]=False
    return matrix

def fix_str(string):
    #replace poistaa "skandi"-merkit
    return string.replace("\xe4", "a").replace("\xe5", "a").replace("\xf6", "o")

def fix_str_noncompatible_chars_in_unicode(string):
    return string.replace("\x9a","?").replace("\x96","?").replace("\x92","?")