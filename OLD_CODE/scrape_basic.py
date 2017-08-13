"""Usable Functions For Other Parts in the program
scrape_ID_TO_NAME_DICT()
    --> dict
scrape_YRITYS_OLIO_DICT(ID_TO_NAME_DICT)
    --> dict
"""

import requests
from bs4 import BeautifulSoup

from yritys import Yritys



def get_raw_soup(link):
    r=requests.get(link)
    soup=BeautifulSoup(r.text, "html.parser")
    return soup


def scrape_ID_TO_NAME_DICT():
    osingot_url = "http://www.kauppalehti.fi/5/i/porssi/osingot/osinkohistoria.jsp"
    soup=get_raw_soup(osingot_url)
    ID_TO_NAME_DICT=get_yritys_dict(soup)
    return ID_TO_NAME_DICT

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

def scrape_YRITYS_OLIO_DICT(ID_TO_NAME_DICT):
    YRITYS_OLIO_DICT = {}
    All_count = len(ID_TO_NAME_DICT)
    count = 1
    for ID in ID_TO_NAME_DICT:
        yritys = Yritys(ID, ID_TO_NAME_DICT[ID])
        print("Progress: ({:3} / {:3}); Current Company: ".format(count, All_count), yritys)
        yritys.scrape()
        YRITYS_OLIO_DICT[ID]=yritys
        count += 1
    
    return YRITYS_OLIO_DICT
