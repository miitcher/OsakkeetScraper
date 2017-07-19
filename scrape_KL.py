#import webbrowser

from print_and_error_functions import *
from scraping_functions import *
from manage_files import *
from yritys_luokka import *



url_perus = "http://www.kauppalehti.fi/5/i/porssi/"

osingot_url =               url_perus + "osingot/osinkohistoria.jsp"
osingot_yritys_url =        url_perus + "osingot/osinkohistoria.jsp?klid={}"            #ID loppuun!
kurssi_url =                url_perus + "porssikurssit/osake/index.jsp?klid={}"         #ID loppuun!
kurssi_tulostiedot_url =    url_perus + "porssikurssit/osake/tulostiedot.jsp?klid={}"   #ID loppuun!



def scrape_yritys_dict():
    soup=get_raw_soup(osingot_url)
    DICT_yritys=get_yritys_dict(soup)       #    DICT_yritys[ID] = "Yrityksen nimi"
    #dictionary_print(DICT_yritys)
    return DICT_yritys

def scrape_yrityksen_tiedot(ID):
    YRITYKSEN_TIEDOT=[]
    """
    DICT_yritys_osinko_mat, DICT_kurssi, DICT_kuvaus_yrityksesta, DICT_perustiedot_dict, DICT_tunnuslukuja_dict, DICT_toiminnan_laajuus_mat, DICT_kannattavuus_mat, DICT_vakavaraisuus_mat, DICT_maksuvalmius_mat, DICT_sijoittajan_tunnuslukuja_mat
    
    YRITYKSEN_TIEDOT voi kayttaa esim. nain:
    YRITYKSEN_TIEDOT[2] --> "yrityksen kurssi"
    
    DICT_YRITYKSEN_TIEDOT voi kayttaa esim. nain:
    DICT_YRITYKSEN_TIEDOT[ID][2] --> "yrityksen kurssi"
    
    innehall:                                INDEX
        DICT_yritys_osinko_mat={}             0
        
        DICT_kurssi={}                        1
        DICT_kuvaus_yrityksesta={}            2
        DICT_perustiedot_dict={}              3
        DICT_tunnuslukuja_dict={}             4
        
        DICT_toiminnan_laajuus_mat={}         5
        DICT_kannattavuus_mat={}              6
        DICT_vakavaraisuus_mat={}             7
        DICT_maksuvalmius_mat={}              8
        DICT_sijoittajan_tunnuslukuja_mat={}  9
    """
    
    #OSINKO TIEDOT
    url = osingot_yritys_url.format(ID)
    soup=get_raw_soup(url)
    YRITYKSEN_TIEDOT.append(    get_yrityksen_osingot(soup))
    
    #KURSSI TIEDOT
    url = kurssi_url.format(ID)
    soup=get_raw_soup(url)
    
    YRITYKSEN_TIEDOT.append(    get_kurssi(soup, ID))
    YRITYKSEN_TIEDOT.append(    get_kuvaus_yrityksesta(soup, ID))
    YRITYKSEN_TIEDOT.append(    get_perustiedot_dict(soup, ID))
    YRITYKSEN_TIEDOT.append(    get_tunnuslukuja_dict(soup, ID))
    
    #KURSSI TULOSTIEDOT
    url = kurssi_tulostiedot_url.format(ID)
    soup=get_raw_soup(url)
    
    YRITYKSEN_TIEDOT.append(    get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Toiminnan laajuus"))
    YRITYKSEN_TIEDOT.append(    get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Kannattavuus"))
    YRITYKSEN_TIEDOT.append(    get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Vakavaraisuus"))
    YRITYKSEN_TIEDOT.append(    get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Maksuvalmius"))
    YRITYKSEN_TIEDOT.append(    get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Sijoittajan tunnuslukuja"))
    
    return YRITYKSEN_TIEDOT

def scrape_DICT_YRITYKSEN_TIEDOT_AND_scraped_IDs(DICT_yritys):
    DICT_YRITYKSEN_TIEDOT={}
    scraped_IDs=[]
    for ID in DICT_yritys:
        print(ID, DICT_yritys[ID])
        
        DICT_YRITYKSEN_TIEDOT[ID] = scrape_yrityksen_tiedot(ID)
        scraped_IDs.append(ID)
        
        #break   #GETS JUST ONE COMPPANY WITH BREAK
    
    return DICT_YRITYKSEN_TIEDOT, scraped_IDs














