import logging

import scraping
import storage

logger = logging.getLogger('root')

#import webbrowser # WHAT IS THIS/COULD BE USED FOR ???


# TODO: remove from here, and have only in scraping.py
url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url =               url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url =        url_basic + "osingot/osinkohistoria.jsp?klid={}"            #ID loppuun!
kurssi_url =                url_basic + "porssikurssit/osake/index.jsp?klid={}"         #ID loppuun!
kurssi_tulostiedot_url =    url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"   #ID loppuun!


def scrape_companies(storage_directory):
    logger.debug("Check if company_names is already fetched today")
    company_names = storage.get_today_stored_company_names(storage_directory)

    if not company_names:
        logger.debug("Company names are scraped from Kauppalehti")
        company_names = scraping.scrape_company_names(osingot_url)
        storage.store_company_list(company_names, storage_directory, "names")

    logger.debug("Individual companies data is scraped from Kauppalehti")
    company_list = []
    for ID in company_names:
        logger.debug("ID:{}, Name:{}".format(ID, company_names[ID]))
        company = scraping.Company(ID, company_names[ID])
        company_list.append(company)
        break # so just one company is scraped
    logger.debug("Number of companies scraped: {}".format(len(company_list)))
    """
    print("\nSTR RAW:")
    print(company_list[0].str_raw)
    print("\nSTR METRICS:")
    print(company_list[0]) # .str_metrics
    """
    logger.debug("Scraped companies are stored")
    tsv_filename_raw     = storage.store_company_list(company_list, storage_directory, "raw")
    tsv_filename_metrics = storage.store_company_list(company_list, storage_directory)
    """
    print("\ntsv RAW:")
    print(company_list[0].tsv_raw)
    print("\ntsv METRICS:")
    print(company_list[0].tsv_metrics)
    """
    return tsv_filename_raw, tsv_filename_metrics

def load_companies(filename):
    """
    self.Tiedot=Tiedot_luokka()
    self.Tiedot.set_from_csv_file(filename)
    print("TIEDOT has been loaded from the file: {}".format(filename))
    """
    pass

def print_companies(filename):
    """
    if self.Tiedot:
        for ID in self.Tiedot.scraped_IDs:
            print("{} {}".format(ID, self.Tiedot.DICT_yritys[ID]))
    else:
        print("TIEDOT is missing")
    """
    pass

def print_company(filename, ID):
    """
    if ID in self.Tiedot.scraped_IDs:
        print("{} {}".format(ID, self.Tiedot.DICT_yritys[ID]))
        matrix_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID][0])
        kurssi_tiedot_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
        kurssi_tulostiedot_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
    else:
        print("There is no company scraped with ID: {}".format(ID))
    """
    pass

def filter_companies(filename):
    pass

def organize_companies(filename):
    pass


# TODO: Remove old scrape functions, that are written in scraping.py
'''
def scrape_yritys_dict():
    DICT_yritys=scraping.scrape_company_names(osingot_url)       #    DICT_yritys[ID] = "Yrityksen nimi"
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
'''
