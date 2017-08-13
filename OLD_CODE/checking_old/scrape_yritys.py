import requests
from bs4 import BeautifulSoup



def get_raw_soup(link):
    r=requests.get(link)
    soup=BeautifulSoup(r.text, "html.parser")
    return soup

def fix_str(string):
    # fix_skandinavian_chars_in_string
    string = string.replace("\xe4", "a").replace("\xe5", "a").replace("\xf6", "o")
    string = string.replace("\xc4", "A").replace("\xc5", "A").replace("\xd6", "O")
    
    # fix_noncompatible_chars_in_unicode_in_string(string)
    string = string.replace("\x9a","?").replace("\x96","?").replace("\x92","?")
    
    return string



class Yritys_scraper():
    def __init__(self, ID):
        self.ID = ID
        self.set_soups()
    
    def set_soups(self):
        url_perus = "http://www.kauppalehti.fi/5/i/porssi/"
        
        osingot_yritys_url =        url_perus + "osingot/osinkohistoria.jsp?klid={}".format(self.ID)
        kurssi_url =                url_perus + "porssikurssit/osake/index.jsp?klid={}".format(self.ID)
        kurssi_tulostiedot_url =    url_perus + "porssikurssit/osake/tulostiedot.jsp?klid={}".format(self.ID)
        
        self.soup_osingot = get_raw_soup(osingot_yritys_url)
        self.soup_kurssi  = get_raw_soup(kurssi_url)
        self.soup_tulost  = get_raw_soup(kurssi_tulostiedot_url)
    
    
    def get_yrityksen_osingot(self):
        yrityksen_osingot=["NOT REDY"]
        
        table_tags = self.soup_osingot.find_all('table')
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
                            pass
                    elif i==2 or i==3 or i==5:
                        try:
                            val=float(val)
                        except:
                            pass
                    OYV.append(val)
                
            yrityksen_osingot.append(OYV)
            c+=1
        yrityksen_osingot[0]=True
        return yrityksen_osingot
    
    
    def get_kurssi(self):
        try:
            table_tags = self.soup_kurssi.find_all('table')
            
            kurssi=table_tags[5].find('span').text
            try:
                kurssi=float(kurssi)
            except:
                pass
        except:
            kurssi="FAIL"
            
        return kurssi
    
    def get_kuvaus_yrityksesta(self):
        try:
            class_padding_tags = self.soup_kurssi.find_all(class_="paddings")
            
            for tag in class_padding_tags:
                if tag.parent.h3.text=="Yrityksen perustiedot":
                    kuvaus_yrityksesta = tag.p.text.strip().replace("\n"," ").replace("\r"," ")
                    
                    kuvaus_yrityksesta = fix_str(kuvaus_yrityksesta)
                    return kuvaus_yrityksesta
            
            kuvaus_yrityksesta="FAIL"
        except:
            kuvaus_yrityksesta="FAIL"
        return kuvaus_yrityksesta
    
    def get_perustiedot_dict(self):
        perustiedot_dict={}
        try:
            TAG = self.get_perustiedot_table_TAG()
            
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
                    if type(val) == str:
                        val = fix_str(val)
                    perustiedot_dict[fix_str(key)]=val
                    
                    strs=td_tags[2].text.split("\n")
                    [key, val]=strs[1].split(":")
                    if type(val) == str:
                        val = fix_str(val)
                    perustiedot_dict[fix_str(key)]=val
                    
                    [key, val]=strs[2].split(":")
                    if type(val) == str:
                        val = fix_str(val)
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
                            pass
                    
                    if type(val) == str:
                        val = fix_str(val)
                    
                    perustiedot_dict[fix_str(key)] = val
            
            perustiedot_dict[0]=True
        except:
            perustiedot_dict[0]=False
        return perustiedot_dict
    
    def get_perustiedot_table_TAG(self):
        try:
            class_is_TSBD = self.soup_kurssi.find_all(class_="table_stock_basic_details")
            
            for tag in class_is_TSBD:
                try:
                    if tag.parent.parent.h3.text.strip() == "Osakkeen perustiedot":
                        return tag
                except:
                    pass
        except:
            pass
        return -1
    
    def get_tunnuslukuja_dict(self):
        tunnuslukuja_dict={}
        try:
            TAG = self.get_tunnuslukuja_table_TAG()
            
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
                        pass
                elif c==5:
                    try:
                        parts=val.split()
                        val=float(parts[0])
                        k=parts[1].split(".")
                        key=key + " ({}. EUR)".format(k[0])
                    except:
                        pass
                else:
                    try:
                        parts=val.split()
                        val=float(parts[0])
                        key=key + " (EUR)"
                    except:
                        pass
                
                tunnuslukuja_dict[fix_str(key)]=val
                c+=1
            
            tunnuslukuja_dict[0]=True
        except:
            tunnuslukuja_dict[0]=False
        return tunnuslukuja_dict
    
    def get_tunnuslukuja_table_TAG(self):
        try:
            table_tags = self.soup_kurssi.find_all('table')
            
            for tag in table_tags:
                try:
                    if tag.parent.p.text.strip() == "Tunnuslukuja":
                        return tag
                except:
                    pass
        except:
            pass
        return -1
    
    
    def get_KURSSI_TULOSTIEDOT_mat(self, otsikko):
        matrix=["NOT REDY"]
        try:
            TAG = self.get_KURSSI_TULOSTIEDOT_table_TAG(otsikko)
            
            if TAG == -1:
                matrix[0]=False
                return matrix
            
            tr_tags=TAG.find_all('tr')
            r=0 #rivi
            for i in tr_tags:
                td_tags=i.find_all('td')
                
                rivi=[]
                s=0 # sarake
                for j in td_tags:
                    if r==0:
                        rivi.append("VUOSI")
                        r+=1
                    else:
                        val=fix_str(j.text.strip())
                        if s>0:
                            val=val.replace(",", ".")
                        s+=1
                        try:
                            val=float(val.replace("\xa0",""))
                        except:
                            pass
                        rivi.append(val)
                
                matrix.append(rivi)
            
            matrix[0]=True
        except:
            matrix[0]=False
        return matrix
    
    def get_KURSSI_TULOSTIEDOT_table_TAG(self, otsikko):
        try:
            table_tags = self.soup_tulost.find_all(class_="table_stockexchange")
            
            for tag in table_tags:
                try:
                    if tag.parent.h3.text.strip() == otsikko:
                        return tag
                except:
                    pass
        except:
            pass
        return -1
