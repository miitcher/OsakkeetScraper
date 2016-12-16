import requests
from bs4 import BeautifulSoup

from print_and_error_functions import *


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




