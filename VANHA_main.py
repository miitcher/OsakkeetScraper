import os
import webbrowser

from print_and_error_functions import *
from scraping_functions import *
from write_files import *
from yritys_luokka import *


def manage_file_folder():
    #Creates a "Files"-folder if one does not exist.
    if not os.path.isdir("Files"):
        os.makedirs("Files")
        print('"Files" folder created')


def vanha_main():
    manage_file_folder()
    
    url_perus = "http://www.kauppalehti.fi/5/i/porssi/"
    
    osingot_url =               url_perus + "osingot/osinkohistoria.jsp"
    osingot_yritys_url =        url_perus + "osingot/osinkohistoria.jsp?klid={}"            #ID loppuun!
    kurssi_url =                url_perus + "porssikurssit/osake/index.jsp?klid={}"         #ID loppuun!
    kurssi_tulostiedot_url =    url_perus + "porssikurssit/osake/tulostiedot.jsp?klid={}"   #ID loppuun!
    
    
    print("------------YRITYS DICTIONARY------------")
    soup=get_raw_soup(osingot_url)
    DICT_yritys=get_yritys_dict(soup)       #    DICT_yritys[ID] = "Yrityksen nimi"
    #dictionary_print(DICT_yritys)
    
    
    print("\n------------YRITYS OSINKO TIEDOT------------")
    yritys_osinko_dict={}                   #    yritys_osinko_dict[ID] = "Lista yrityksen osingoista"
    for ID in DICT_yritys:
        ID=1901
        #print(ID, DICT_yritys[ID])
        
        url = osingot_yritys_url.format(ID)
        soup=get_raw_soup(url)
        yritys_osinko_dict[ID]=get_yrityksen_osingot(soup)
        break   #GETS JUST ONE COMPPANY WITH BREAK
    matrix_print(yritys_osinko_dict, ID)
    
    
    #print("\n------------YRITYS OSINKO TIEDOT CSV-TIEDOSTOON------------")
    #OSINKO_write_csv(yritys_osinko_dict, DICT_yritys)
    
    
    print("\n------------YRITYS KURSSI TIEDOT------------")
    DICT_kurssi={}                          #    DICT_kurssi[ID] = "Vastaavat tiedot"
    DICT_kuvaus_yrityksesta={}              #    --||--
    DICT_perustiedot_dict={}                #    --||--
    DICT_tunnuslukuja_dict={}               #    --||--
    
    for ID in DICT_yritys:
        ID=1901
        #print(ID, DICT_yritys[ID])
        url = kurssi_url.format(ID)
        soup=get_raw_soup(url)
        
        DICT_kurssi[ID]             = get_kurssi(soup, ID)
        DICT_kuvaus_yrityksesta[ID] = get_kuvaus_yrityksesta(soup, ID)
        DICT_perustiedot_dict[ID]   = get_perustiedot_dict(soup, ID)
        DICT_tunnuslukuja_dict[ID]  = get_tunnuslukuja_dict(soup, ID)
        
        kurssi_tiedot_print(ID, DICT_kurssi, DICT_kuvaus_yrityksesta, DICT_perustiedot_dict, DICT_tunnuslukuja_dict)
        break   #GETS JUST ONE COMPPANY WITH BREAK
    
    
    print("\n------------YRITYS KURSSI TULOSTIEDOT------------")
    DICT_toiminnan_laajuus_mat={}           #    DICT_toiminnan_laajuus_mat[ID] = "Vastaavat tiedot (matriisina)"
    DICT_kannattavuus_mat={}                #    --||--
    DICT_vakavaraisuus_mat={}               #    --||--
    DICT_maksuvalmius_mat={}                #    --||--
    DICT_sijoittajan_tunnuslukuja_mat={}    #    --||--
    
    for ID in DICT_yritys:
        ID=1901
        #print(ID, DICT_yritys[ID])
        url = kurssi_tulostiedot_url.format(ID)
        soup=get_raw_soup(url)
        
        DICT_toiminnan_laajuus_mat[ID]         = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Toiminnan laajuus")
        DICT_kannattavuus_mat[ID]              = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Kannattavuus")
        DICT_vakavaraisuus_mat[ID]             = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Vakavaraisuus")
        DICT_maksuvalmius_mat[ID]              = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Maksuvalmius")
        DICT_sijoittajan_tunnuslukuja_mat[ID]  = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Sijoittajan tunnuslukuja")
        
        kurssi_tulostiedot_print(ID, DICT_toiminnan_laajuus_mat, DICT_kannattavuus_mat, DICT_vakavaraisuus_mat, DICT_maksuvalmius_mat, DICT_sijoittajan_tunnuslukuja_mat) 
        break   #GETS JUST ONE COMPPANY WITH BREAK
    
    
    
    #print("\n------------ERROR COUNTS------------")
    #errors_counts_print()
    
    
    
    print("\n------------TESTAUS------------")
    
    #KURSSI_TIEDOT_write_csv(ID, DICT_yritys, DICT_kurssi, DICT_kuvaus_yrityksesta, DICT_perustiedot_dict, DICT_tunnuslukuja_dict)
    
    
    """
    for ID in KNOWN_MISSING_KURSSI_TULOSTIEDOT_table_TAG:
        print(ID, DICT_yritys[ID])
        url = kurssi_url.format(ID)
        webbrowser.open(url)
    """
    
    
    print("\n------------END------------")


def main():
    manage_file_folder()
    
    url_perus = "http://www.kauppalehti.fi/5/i/porssi/"
    
    osingot_url =               url_perus + "osingot/osinkohistoria.jsp"
    osingot_yritys_url =        url_perus + "osingot/osinkohistoria.jsp?klid={}"            #ID loppuun!
    kurssi_url =                url_perus + "porssikurssit/osake/index.jsp?klid={}"         #ID loppuun!
    kurssi_tulostiedot_url =    url_perus + "porssikurssit/osake/tulostiedot.jsp?klid={}"   #ID loppuun!
    
    
    print("------------YRITYS DICTIONARY------------")
    soup=get_raw_soup(osingot_url)
    DICT_yritys=get_yritys_dict(soup)       #    DICT_yritys[ID] = "Yrityksen nimi"
    #dictionary_print(DICT_yritys)
    
    
    
    print("------------TIETOJEN KAAPIMINEN------------")
    yritys_osinko_dict={}
    
    DICT_kurssi={}
    DICT_kuvaus_yrityksesta={}
    DICT_perustiedot_dict={}
    DICT_tunnuslukuja_dict={}
    
    DICT_toiminnan_laajuus_mat={}
    DICT_kannattavuus_mat={}
    DICT_vakavaraisuus_mat={}
    DICT_maksuvalmius_mat={}
    DICT_sijoittajan_tunnuslukuja_mat={}
    
    for ID in DICT_yritys:
        #ID=1901
        ID=1971
        print(ID, DICT_yritys[ID])
        
        #OSINKO TIEDOT
        url = osingot_yritys_url.format(ID)
        soup=get_raw_soup(url)
        yritys_osinko_dict[ID]=get_yrityksen_osingot(soup)
        
        #KURSSI TIEDOT
        url = kurssi_url.format(ID)
        soup=get_raw_soup(url)
        
        DICT_kurssi[ID]             = get_kurssi(soup, ID)
        DICT_kuvaus_yrityksesta[ID] = get_kuvaus_yrityksesta(soup, ID)
        DICT_perustiedot_dict[ID]   = get_perustiedot_dict(soup, ID)
        DICT_tunnuslukuja_dict[ID]  = get_tunnuslukuja_dict(soup, ID)
        
        #KURSSI TULOSTIEDOT
        url = kurssi_tulostiedot_url.format(ID)
        soup=get_raw_soup(url)
        
        DICT_toiminnan_laajuus_mat[ID]         = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Toiminnan laajuus")
        DICT_kannattavuus_mat[ID]              = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Kannattavuus")
        DICT_vakavaraisuus_mat[ID]             = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Vakavaraisuus")
        DICT_maksuvalmius_mat[ID]              = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Maksuvalmius")
        DICT_sijoittajan_tunnuslukuja_mat[ID]  = get_KURSSI_TULOSTIEDOT_mat(soup, ID, "Sijoittajan tunnuslukuja")
        
        
        #kurssi_tiedot_print(ID, DICT_kurssi, DICT_kuvaus_yrityksesta, DICT_perustiedot_dict, DICT_tunnuslukuja_dict)
        #kurssi_tulostiedot_print(ID, DICT_toiminnan_laajuus_mat, DICT_kannattavuus_mat, DICT_vakavaraisuus_mat, DICT_maksuvalmius_mat, DICT_sijoittajan_tunnuslukuja_mat) 
        break   #GETS JUST ONE COMPPANY WITH BREAK
        
    #matrix_print(yritys_osinko_dict, ID)
    """for i in yritys_osinko_dict[ID]:
        print(i)"""
    
    print("\n------------LUOKKINEN LUONTI------------")
    Tiedot=Tiedot_luokka(DICT_yritys)
    
    Tiedot.set_osinko_tiedot(yritys_osinko_dict)
    Tiedot.set_kurssi_tiedot(DICT_kurssi, DICT_kuvaus_yrityksesta, DICT_perustiedot_dict, DICT_tunnuslukuja_dict)
    Tiedot.set_kurssi_tulostiedot(DICT_toiminnan_laajuus_mat, DICT_kannattavuus_mat, DICT_vakavaraisuus_mat, DICT_maksuvalmius_mat, DICT_sijoittajan_tunnuslukuja_mat)
    
    yritys_OLIO_dict={}
    for ID in DICT_yritys:
        #ID=1901
        ID=1971
        print(ID, DICT_yritys[ID])
        
        yritys=Yritys(ID, Tiedot)
        yritys.set_yritysksen_tiedot()
        yritys_OLIO_dict[ID]=yritys
        break
    
    
    """
    print("\n------------WRITING FILES------------")
    OSINKO_write_csv(yritys_osinko_dict, DICT_yritys)
    KURSSI_TIEDOT_write_csv(ID, DICT_yritys, DICT_kurssi, DICT_kuvaus_yrityksesta, DICT_perustiedot_dict, DICT_tunnuslukuja_dict)
    """
    
    
    """
    print("\n------------TESTAUS------------")
    
    for ID in KNOWN_MISSING_tunnuslukuja_table_tag_LIST:
        print(ID, DICT_yritys[ID])
        url = kurssi_url.format(ID)
        webbrowser.open(url)
    """
    
    
    print("\n------------ERROR COUNTS------------")
    errors_counts_print()
    
    
    print("\n------------END------------")

main()






















