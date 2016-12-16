from print_and_error_functions import *
from manage_files import *


class Tiedot_luokka():
    def __init__(self):
        pass
    
    def set_from_scrape(self, DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys):
        self.DICT_YRITYKSEN_TIEDOT = DICT_YRITYKSEN_TIEDOT
        self.scraped_IDs = scraped_IDs
        self.DICT_yritys=DICT_yritys
    
    def set_from_csv_file(self, filename):
        DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys = DICT_YRITYKSEN_TIEDOT_csv_file_READ(filename)
        
        self.DICT_YRITYKSEN_TIEDOT = DICT_YRITYKSEN_TIEDOT
        self.scraped_IDs = scraped_IDs
        self.DICT_yritys = DICT_yritys
    
    def save_to_csv_file(self):
        DICT_YRITYKSEN_TIEDOT_csv_file_WRITE(self.DICT_YRITYKSEN_TIEDOT, self.scraped_IDs, self.DICT_yritys)


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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    