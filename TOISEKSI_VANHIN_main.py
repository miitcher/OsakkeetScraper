import os
import webbrowser

from print_and_error_functions import *
from scraping_functions import *
from manage_files import *
from yritys_luokka import *

from scrape_KL import *


def manage_file_folder():
    #Creates a "Files"-folder if one does not exist.
    if not os.path.isdir("Files"):
        os.makedirs("Files")
        print('"Files" folder created')

def scrape_and_store_to_csv_file():
    print("------------YRITYS DICTIONARY------------")
    DICT_yritys = scrape_yritys_dict()
    #dictionary_print(DICT_yritys)
    
    
    print("------------TIETOJEN KAAPIMINEN------------")
    DICT_YRITYKSEN_TIEDOT, scraped_IDs = scrape_DICT_YRITYKSEN_TIEDOT_AND_scraped_IDs(DICT_yritys)
    ID=2048
    matrix_print(DICT_YRITYKSEN_TIEDOT[ID][0])
    kurssi_tiedot_print(DICT_YRITYKSEN_TIEDOT[ID])
    kurssi_tulostiedot_print(DICT_YRITYKSEN_TIEDOT[ID])
    
    """
    print("\n------------LUOKKINEN LUONTI ja TALLENNUS------------")
    Tiedot=Tiedot_luokka()
    Tiedot.set_from_scrape(DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys)
    Tiedot.save_to_csv_file()
    """
    
    print("\n------------ERROR COUNTS------------")
    #suunnattu enemman scrapingiin
    errors_counts_print()
    
    print("\n------------END------------")


def main():
    manage_file_folder()
    
    
    print("\n------------LUOKKINEN LUONTI ja TALLENNUS------------")
    filename="Files\\" + "DICT_YRITYKSEN_TIEDOT-2016_6_17--22_10_25_317054.csv"
    Tiedot=Tiedot_luokka()
    Tiedot.set_from_csv_file(filename)
    
    ID=2048
    matrix_print(Tiedot.DICT_YRITYKSEN_TIEDOT[ID][0])
    kurssi_tiedot_print(Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
    kurssi_tulostiedot_print(Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
    
    
    """
    DICT_YRITYKSEN_TIEDOT = Tiedot.DICT_YRITYKSEN_TIEDOT
    scraped_IDs =           Tiedot.scraped_IDs
    DICT_yritys =           Tiedot.DICT_yritys
    
    yritys_OLIO_dict={}
    for ID in scraped_IDs:
        print(ID, DICT_yritys[ID])
        
        yritys=Yritys(ID, Tiedot)
        yritys_OLIO_dict[ID]=yritys
        #break
    """
    
    """
    print("\n------------TESTAUS------------")
    
    for ID in KNOWN_MISSING_tunnuslukuja_table_tag_LIST:
        print(ID, DICT_yritys[ID])
        url = kurssi_url.format(ID)
        webbrowser.open(url)
    """
    
    
    print("\n------------END------------")


scrape_and_store_to_csv_file()
#main()






















