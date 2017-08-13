from scrape_yritys import Yritys_scraper



def dict_print(dic):
    print("KEY\tVALUE")
    for KEY in dic:
        print("[{}]\t[{}]".format(KEY, dic[KEY]))



class Yritys():
    def __init__(self, ID, NIMI):
        self.ID=ID
        self.nimi=NIMI
        
        #FOR LOADING FROM CSV-FILE
        self.yritys_osinko_mat = []
        
        self.kurssi =                None
        self.kuvaus_yrityksesta =    None
        self.perustiedot_dict =      {}
        self.tunnuslukuja_dict =     {}
        
        self.toiminnan_laajuus_mat =        []
        self.kannattavuus_mat =             []
        self.vakavaraisuus_mat =            []
        self.maksuvalmius_mat =             []
        self.sijoittajan_tunnuslukuja_mat = []
        
        
        #FOR SORT
        self.Gearing_listing=0
        self.OVA_listing=0
        self.PB_listing=0
        self.PE_listing=0
        self.OT_listing=0
        self.ROE_listing=0
        self.OT_ka_listing=0
        
        self.listing_FINAL=-1
        self.RANK=-1
        
        self.Failed_sort=False
        
        self.ERROR_list = []
    
    def __repr__(self):
        return repr((self.ID, self.nimi))
    
    def scrape(self):
        YS = Yritys_scraper(self.ID)
        
        #OSINKO TIEDOT
        self.yritys_osinko_mat    = YS.get_yrityksen_osingot()
        
        
        #KURSSI TIEDOT
        self.kurssi               = YS.get_kurssi()
        if self.kurssi == "FAIL":
            self.ERROR_list.append("ScrapeError: {}".format("kurssi"))
        
        self.kuvaus_yrityksesta   = YS.get_kuvaus_yrityksesta()
        if self.kuvaus_yrityksesta == "FAIL":
            self.ERROR_list.append("ScrapeError: {}".format("kuvaus_yrityksesta"))
        
        self.perustiedot_dict     = YS.get_perustiedot_dict()
        if not self.perustiedot_dict[0]:
            self.ERROR_list.append("ScrapeError: {}".format("perustiedot_dict"))
        
        self.tunnuslukuja_dict    = YS.get_tunnuslukuja_dict()
        if not self.tunnuslukuja_dict[0]:
            self.ERROR_list.append("ScrapeError: {}".format("tunnuslukuja_dict"))
        
        
        #KURSSI TULOSTIEDOT
        self.toiminnan_laajuus_mat        = YS.get_KURSSI_TULOSTIEDOT_mat("Toiminnan laajuus")
        if not self.toiminnan_laajuus_mat[0]:
            self.ERROR_list.append("ScrapeError: {}".format("toiminnan_laajuus_mat"))
        
        self.kannattavuus_mat             = YS.get_KURSSI_TULOSTIEDOT_mat("Kannattavuus")
        if not self.kannattavuus_mat[0]:
            self.ERROR_list.append("ScrapeError: {}".format("kannattavuus_mat"))
        
        self.vakavaraisuus_mat            = YS.get_KURSSI_TULOSTIEDOT_mat("Vakavaraisuus")
        if not self.vakavaraisuus_mat[0]:
            self.ERROR_list.append("ScrapeError: {}".format("vakavaraisuus_mat"))
        
        self.maksuvalmius_mat             = YS.get_KURSSI_TULOSTIEDOT_mat("Maksuvalmius")
        if not self.maksuvalmius_mat[0]:
            self.ERROR_list.append("ScrapeError: {}".format("maksuvalmius_mat"))
        
        self.sijoittajan_tunnuslukuja_mat = YS.get_KURSSI_TULOSTIEDOT_mat("Sijoittajan tunnuslukuja")
        if not self.sijoittajan_tunnuslukuja_mat[0]:
            self.ERROR_list.append("ScrapeError: {}".format("sijoittajan_tunnuslukuja_mat"))
    
    def prosess(self):
        self.format()
        self.validate()
        self.trim()
        self.set_info_for_LINE_print()
    
    
    def format(self):
        #POIMI TIEDOT
        self.set_osinko_tiedot()
        self.set_kurssi_tiedot()
        self.set_kurssi_tulostiedot()
        
        #LASKE NYKYISIA LUKUJA
        self.laske_tunnuslukuja()
        
        #ASETA KAYTTO TUNNUSLUVUT
        self.set_kaytto_tunnusluvut()
    
    def set_osinko_tiedot(self):
        """SAADUT TUNNUSLUVUT
        self.vuoden_osingot_lista
        self.viime_osinko
        """
        
        if self.yritys_osinko_mat[0]:
            self.vuoden_osingot_lista=[0,0,0,0,0]
            c=0
            for r in self.yritys_osinko_mat:
                if c>0:
                    if r[0]==2016:
                        self.vuoden_osingot_lista[0] += r[2]
                    elif r[0]==2015:
                        self.vuoden_osingot_lista[1] += r[2]
                    elif r[0]==2014:
                        self.vuoden_osingot_lista[2] += r[2]
                    elif r[0]==2013:
                        self.vuoden_osingot_lista[3] += r[2]
                    elif r[0]==2012:
                        self.vuoden_osingot_lista[4] += r[2]
                c+=1
            
            self.viime_osinko = self.vuoden_osingot_lista[0]
        else:
            self.ERROR_list.append("FormatError: {}".format("yritys_osinko_mat"))
            self.vuoden_osingot_lista=False
            self.viime_osinko=False
    
    def set_kurssi_tiedot(self):
        """SAADUT TUNNUSLUVUT
        self.nykyinen_kurssi
        self.kuvaus
        self.toimiala
        self.toimialaluokka
        self.markkina_arvo
        """
        
        #nykyinen kurssi
        val=self.kurssi
        if type(val)==float:
            self.nykyinen_kurssi=val
        else:
            self.ERROR_list.append("FormatError: {}".format("nykyinen_kurssi"))
            self.nykyinen_kurssi=False
        
        #Kuvaus
        self.kuvaus=self.kuvaus_yrityksesta
        
        #Toimiala, Toimialaluokka, Kappaletta osakkeita
        perus_dict=self.perustiedot_dict
        if perus_dict[0]:
            self.toimiala=perus_dict["Toimiala"]
            self.toimialaluokka=perus_dict["Toimialaluokka"]
            try:
                s=perus_dict["Markkina-arvo"]
                a=s.replace("Milj.EUR","")
                self.markkina_arvo=float(a)
            except:
                self.markkina_arvo=False
        else:
            self.ERROR_list.append("FormatError: {}".format("toimiala TAI toimialaluokka"))
            self.toimiala=False
            self.toimialaluokka=False
            self.markkina_arvo=False
    
    def set_kurssi_tulostiedot(self):
        """SAADUT TUNNUSLUVUT
        self.vuodet
        self.ROE
        self.nettotulokset
        
        self.omavaraisuusaste
        self.gearing
        
        self.PB_luku
        self.PE_luku
        self.E_luku
        self.P_luku
        """
        
        ##KANNATTAVUUS
        kann_mat=self.kannattavuus_mat
        if kann_mat[0]:
            #Vuodet
            self.vuodet=[]
            for sarake in range(1,6):
                vuosi=kann_mat[1][sarake]
                if vuosi!="-":
                    self.vuodet.append(vuosi)
            
            #ROE (Oman paaoman tuotto, %)
            self.ROE=self.poimi_arvo_tuolostiedoista(kann_mat, "Oman paaoman tuotto, %", 7, 1)
            
            #Nettotulokset
            self.nettotulokset=[]
            for i in range(1,6):
                val=self.poimi_arvo_tuolostiedoista(kann_mat, "Nettotulos", 4, i)
                if val:
                    self.nettotulokset.append(val)
        else:
            self.ERROR_list.append("FormatError: {}".format("kannattavuus_mat"))
            self.vuodet=False
            self.ROE=False
            self.nettotulokset=False
        
        ##VAKAVARAISUUS
        vaka_mat=self.vakavaraisuus_mat
        if vaka_mat[0]:
            #Omavaraisuusaste, %
            self.omavaraisuusaste=self.poimi_arvo_tuolostiedoista(vaka_mat, "Omavaraisuusaste, %", 2, 1)
            
            #Gearing (Nettovelkaantumisaste, %)
            self.gearing=self.poimi_arvo_tuolostiedoista(vaka_mat, 'Nettovelkaantumisaste, %', 3, 1)
        else:
            self.ERROR_list.append("FormatError: {}".format("vakavaraisuus_mat"))
            self.omavaraisuusaste=False
            self.gearing=False
        
        ##SIJOITTAJAN TUNNUSLUKUJA
        sijo_mat=self.sijoittajan_tunnuslukuja_mat
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
            self.ERROR_list.append("FormatError: {}".format("sijoittajan_tunnuslukuja_mat"))
            self.PB_luku=False
            self.PE_luku=False
            self.E_luku=False
            self.P_luku=False
    
    def poimi_arvo_tuolostiedoista(self, matrix, header, rivi, sarake):
        if matrix[0]:
            vuodet1=['VUOSI', '01/16', '01/15', '01/14', '01/13', '01/12']
            vuodet2=['VUOSI', '12/15', '12/14', '12/13', '12/12', '12/11']
            vuodet3=['VUOSI', '10/15', '10/14', '10/13', '10/12', '10/11']
            vuodet4=['VUOSI', '08/15', '08/14', '08/13', '08/12', '08/11']
            vuodet5=['VUOSI', '12/14', '12/13', '12/12', '12/11', '12/10']
            vuodet6=['VUOSI', '10/16', '10/15', '10/14', '10/13', '10/12']
            
            vuosi=matrix[1][sarake]
            head=matrix[rivi][0]
            if head==header and (vuosi==vuodet1[sarake] or vuosi==vuodet2[sarake] or vuosi==vuodet3[sarake] or vuosi==vuodet4[sarake] or vuosi==vuodet5[sarake] or vuosi==vuodet6[sarake]):
                val=matrix[rivi][sarake]
                if type(val)==float:
                    return val
                elif val=="-":
                    #Kun val on "-"; niin silloin tieto puuttuu. Tama ei ole virhe.
                    return False
                else:
                    self.ERROR_list.append("FormatError: {}".format("{} (Wrong Value), Val=[{}], Type=[{}]".format(header, val, type(val))))
                    return False
            elif vuosi=="-":
                #Kun vuoden kohdalla on "-"; niin silloin tiedot puuttuvat sarakkeesta. Tama ei ole virhe.
                return False
        self.ERROR_list.append("FormatError: {}".format(header))
        return False
    
    def laske_tunnuslukuja(self):
        """SAADUT TUNNUSLUVUT
        self.nykyinen_osinkotuotto_PROCENT
        self.nykyinen_P_luku
        self.P_muutos_kerroin
        self.nykyinen_PB_luku
        self.nykyinen_PE_luku
        
        self.osinkotuotto_keskiarvo_PROCENT
        """
        
        if self.viime_osinko and self.nykyinen_kurssi:
            self.nykyinen_osinkotuotto_PROCENT = round( 100* self.viime_osinko / self.nykyinen_kurssi, 2)
        else:
            self.nykyinen_osinkotuotto_PROCENT=False
        
        if self.markkina_arvo:
            self.nykyinen_P_luku = self.markkina_arvo
        else:
            self.nykyinen_P_luku=False
        
        if self.nykyinen_P_luku and self.P_luku:
            self.P_muutos_kerroin = round( self.nykyinen_P_luku / self.P_luku, 4)
            self.P_muutos_kerroin = float(self.P_muutos_kerroin)
        else:
            self.P_muutos_kerroin=False
        
        if type(self.P_muutos_kerroin)==float and self.PB_luku:
            self.nykyinen_PB_luku = round( self.P_muutos_kerroin * self.PB_luku, 2)
        else:
            self.nykyinen_PB_luku=False
        
        if type(self.P_muutos_kerroin)==float and self.PE_luku:
            self.nykyinen_PE_luku = round( self.P_muutos_kerroin * self.PE_luku, 2)
        else:
            self.nykyinen_PE_luku=False
        
        #keskiarvo osinkotuotolle 5 vuoden ajalta
        if self.vuoden_osingot_lista and self.nykyinen_kurssi:
            su=0
            for i in self.vuoden_osingot_lista:
                su += i
            self.osinkotuotto_keskiarvo_PROCENT = round( 100*su / (5*self.nykyinen_kurssi), 2)
            self.osinkotuotto_keskiarvo_PROCENT = float(self.osinkotuotto_keskiarvo_PROCENT)
        else:
            self.osinkotuotto_keskiarvo_PROCENT=False
    
    def set_kaytto_tunnusluvut(self):
        """SAADUT TUNNUSLUVUT
        self.PB_kaytto
        self.PE_kaytto
        """
        
        #ASETA KAYTETTAVAT LASKETUT TUNNUSLUVUT
        if self.nykyinen_PB_luku:
            self.PB_kaytto = self.nykyinen_PB_luku
        else:
            self.PB_kaytto = self.PB_luku
        
        if self.nykyinen_PE_luku:
            self.PE_kaytto = self.nykyinen_PE_luku
        else:
            self.PE_kaytto = self.PE_luku
    
    
    def validate(self):
        pass
    
    
    def trim(self):
        """SAADUT BOOLEAANIT
        self.KAR_gearing
        self.KAR_omavaraisuusaste
        self.KAR_ROE
        self.KAR_viisi_vuotta_osinkoa
        self.KAR_tulokset_nousee_viisi_vuotta
        self.KARSINTA_LAPI
        """
        
        #TRIM RAJA-ARVOT
        GEARING_MAX = 100
        OVA_MIN     = 40
        ROE_MIN     = 10
        
        
        #RAHOITUSRAKENNE (gearing <GEARING_MAX%, omavaraisuusaste >OVA_MIN%)
        if self.gearing:
            if self.gearing < GEARING_MAX:
                self.KAR_gearing=True
            else:
                self.KAR_gearing=False
        else:
            self.KAR_gearing=False
        
        if self.omavaraisuusaste:
            if self.omavaraisuusaste > OVA_MIN:
                self.KAR_omavaraisuusaste=True
            else:
                self.KAR_omavaraisuusaste=False
        else:
            self.KAR_omavaraisuusaste=False
        
        #TUOTTO (ROE >ROE_MIN%)
        if self.ROE:
            if self.ROE > ROE_MIN:
                self.KAR_ROE=True
            else:
                self.KAR_ROE=False
        else:
            self.KAR_ROE=False
        
        #OSINKO (osinkotuotto >0 viisi vuotta)
        self.KAR_viisi_vuotta_osinkoa=True
        if self.vuoden_osingot_lista:
            for i in self.vuoden_osingot_lista:
                if i==0:
                    self.KAR_viisi_vuotta_osinkoa=False
                    break
        else:
            self.KAR_viisi_vuotta_osinkoa=False
            self.osinkotuotto_keskiarvo_PROCENT=False
        
        #TULOS (korkeintaan 1 tuloksen heikennys viitena vuotena)
        c_heik=0
        if self.nettotulokset:
            le = len(self.nettotulokset) -1
            while le>0:
                if self.nettotulokset[le-1] < self.nettotulokset[le]:
                    c_heik+=1
                le-=1
            
            if c_heik >1:
                self.KAR_tulokset_nousee_viisi_vuotta=False
            else:
                self.KAR_tulokset_nousee_viisi_vuotta=True
        else:
            self.KAR_tulokset_nousee_viisi_vuotta=False
        
        
        #LOPULLINEN KARSINTA
        if self.KAR_gearing and self.KAR_omavaraisuusaste and self.KAR_ROE and self.KAR_viisi_vuotta_osinkoa and self.KAR_tulokset_nousee_viisi_vuotta:
            self.KARSINTA_LAPI=True
        else:
            self.KARSINTA_LAPI=False
    
    
    def set_info_for_LINE_print(self):
        """SAADUT INFOT
        self.trimFail
        self.trimFailCount
        
        self.toimiala_lyhenne
        """
        
        self.set_trimFail_AND_trimFailCount()
        self.set_Toimiala_lyhenne()
    
    def set_trimFail_AND_trimFailCount(self):
        #TRIMFAIL
        self.trimFail=""
        
        if not self.KAR_gearing:
            self.trimFail += "G"
        if not self.KAR_omavaraisuusaste:
            self.trimFail += "O"
        if not self.KAR_ROE:
            self.trimFail += "R"
        if not self.KAR_viisi_vuotta_osinkoa:
            self.trimFail += "J"
        if not self.KAR_tulokset_nousee_viisi_vuotta:
            self.trimFail += "T"
        
        #TRIMFAILCOUNT
        self.trimFailCount=len(self.trimFail)
    
    def set_Toimiala_lyhenne(self):
        listaToimialoista = ["Kulutuspalvelut","Kulutustavarat","Perusteollisuus","Rahoitus",\
        "Teknologia","Teollisuustuotteet ja -palvelut","Terveydenhuolto",\
        "Tietoliikennepalvelut","Yleishyodylliset palvelut","Oljy ja kaasu"]
        
        if self.toimiala == listaToimialoista[0]:
            self.toimiala_lyhenne="KuPa"
        elif self.toimiala == listaToimialoista[1]:
            self.toimiala_lyhenne="KuTa"
        elif self.toimiala == listaToimialoista[2]:
            self.toimiala_lyhenne="PeTe"
        elif self.toimiala == listaToimialoista[3]:
            self.toimiala_lyhenne="Raho"
        elif self.toimiala == listaToimialoista[4]:
            self.toimiala_lyhenne="Tekn"
        elif self.toimiala == listaToimialoista[5]:
            self.toimiala_lyhenne="TePa"
        elif self.toimiala == listaToimialoista[6]:
            self.toimiala_lyhenne="TeHu"
        elif self.toimiala == listaToimialoista[7]:
            self.toimiala_lyhenne="TiLiPa"
        elif self.toimiala == listaToimialoista[8]:
            self.toimiala_lyhenne="YlPa"
        elif self.toimiala == listaToimialoista[9]:
            self.toimiala_lyhenne="OlKa"
        else:
            self.toimiala_lyhenne="????"
    
    
    def RAW_print(self):
        print("\n{} {}\t+RAW Companys Info".format(self.ID, self.nimi))
        
        print("\n+++++OSINGOT PRINT")
        for i in self.yritys_osinko_mat:
            print(i)
        print("+++++\n")
        
        print("\n+++++TIEDOT PRINT")
        print("+ KURSSI: {}\n".format(self.kurssi))
        print("+ KUVAUS YRITYKSESTA:\n{}\n".format(self.kuvaus_yrityksesta))
        print("+ PERUSTIEDOT DICTIONARY:")
        dict_print(self.perustiedot_dict)
        print("\n+ TUNNUSLUKUJA DICTIONARY:")
        dict_print(self.tunnuslukuja_dict)
        print("+++++\n")
        
        print("\n+++++TULOSTIEDOT PRINT")
        print("+ TOIMINNAN LAAJUUS MATRIISI:")
        for i in self.toiminnan_laajuus_mat:
            print(i)
        print("\n+ KANNATTAVUUS MATRIISI:")
        for i in self.kannattavuus_mat:
            print(i)
        print("\n+ VAKAVARAISUUS MATRIISI:")
        for i in self.vakavaraisuus_mat:
            print(i)
        print("\n+ MAKSUVALMIUS MATRIISI:")
        for i in self.maksuvalmius_mat:
            print(i)
        print("\n+ SIJOITTAJAN TUNNUSLUKUJA MATRIISI:")
        for i in self.sijoittajan_tunnuslukuja_mat:
            print(i)
        print("+++++")
    
    def FORMATED_print(self):
        print("\n{} {}\t+FORMATED Companys Info".format(self.ID, self.nimi))
        
        print("\n+++++TIEDOT PRINT")
        print("\tPOIMITUT ARVOT:")
        print("nykyinen_kurssi: ", self.nykyinen_kurssi)
        print("viime_osinko (EUR): ", self.viime_osinko)
        
        print("\nomavaraisuusaste: ", self.omavaraisuusaste)
        print("gearing: ", self.gearing)
        print("markkina_arvo: ", self.markkina_arvo)
        print("vuodet: ", self.vuodet)
        print("nettotulokset: ", self.nettotulokset)
        print("vuoden_osingot_lista: ", self.vuoden_osingot_lista)
        
        print("\nROE: ", self.ROE)
        print("P_luku: ", self.P_luku)
        print("E_luku: ", self.E_luku)
        print("PB_luku: ", self.PB_luku)
        print("PE_luku: ", self.PE_luku)
        
        print("\nToimiala: ", self.toimiala)
        print("Toimialaluokka: ", self.toimialaluokka)
        print("Kuvaus: ", self.kuvaus)
        
        
        print("\n\n\tLASKETTUA:")
        print("nykyinen_osinkotuotto_PROCENT: ", self.nykyinen_osinkotuotto_PROCENT)
        print("nykyinen_P_luku: ", self.nykyinen_P_luku)
        print("P_muutos_kerroin: ", self.P_muutos_kerroin)
        print("nykyinen_PB_luku: ", self.nykyinen_PB_luku)
        print("nykyinen_PE_luku: ", self.nykyinen_PE_luku)
        print("osinkotuotto_keskiarvo_PROCENT: ", self.osinkotuotto_keskiarvo_PROCENT)
        print("+++++\n")
        
        
        print("\n+++++KIINNOSTAVAT TUNNUSLUVUT:")
        print("Nimi\t\tLuku\tVanha\n\tKarsintaa varten:")
        print("Gearing\t\t{}".format(self.gearing))
        print("Omavaraisuusas.\t{}".format(self.omavaraisuusaste))
        print("ROE\t\t{}".format(self.ROE))
        if self.vuoden_osingot_lista:
            v=16
            for i in self.vuoden_osingot_lista:
                print("V. osingot ({})\t{}".format(v, i))
                v-=1
        if self.nettotulokset:
            c=0
            for i in self.nettotulokset:
                try:
                    vuosi=self.vuodet[c]
                except IndexError:
                    vuosi=False
                print("N.tulos ({})\t{}".format(vuosi, i))
                c+=1
        else:
            print("N.tulos mat\t{}".format(self.nettotulokset))
        print("\tJarjestamista varten:")
        print("PB_luku\t\t{}\t{}".format(self.nykyinen_PB_luku, self.PB_luku))
        print("PE_luku\t\t{}\t{}".format(self.nykyinen_PE_luku, self.PE_luku))
        print("Osinkot. (%)\t{}".format(self.nykyinen_osinkotuotto_PROCENT))
        print("ROE\t\t{}".format(self.ROE))
        print("+++++")
    
    def TRIMMED_print(self):
        print("\n+++++KARSINTA TIEDOT:")
        print("KAR_gearing\t\t{}".format(self.KAR_gearing))
        print("KAR_omavaraisuusaste\t{}".format(self.KAR_omavaraisuusaste))
        print("KAR_ROE\t\t\t{}".format(self.KAR_ROE))
        print("KAR_5v._osinkoa\t\t{}".format(self.KAR_viisi_vuotta_osinkoa))
        print("KAR_tulokset_nousee_5v.\t{}".format(self.KAR_tulokset_nousee_viisi_vuotta))
        
        print("\nKARSINTA_LAPI\t\t{}".format(self.KARSINTA_LAPI))
        print("+++++")
    
    def SORTED_print(self):
        print("\n+++++SORT TIEDOT:")
        print("\t\tLISTING\tTUNNUSLUKU")
        print("Gearing\t\t{}\t{}".format(self.Gearing_listing, self.gearing))
        print("OVA\t\t{}\t{}".format(self.OVA_listing, self.omavaraisuusaste))
        print("P/B\t\t{}\t{}".format(self.PB_listing, self.PB_kaytto))
        print("P/E\t\t{}\t{}".format(self.PE_listing, self.PE_kaytto))
        print("Osinkot.\t{}\t{} %".format(self.OT_listing, self.nykyinen_osinkotuotto_PROCENT))
        print("ROE\t\t{}\t{}".format(self.ROE_listing, self.ROE))
        print("Osinkot. ka 5v\t{}\t{}".format(self.OT_ka_listing, self.osinkotuotto_keskiarvo_PROCENT))
        
        print("\nListing_FINAL\t{}".format(self.listing_FINAL))
        print("RANK\t\t{}".format(self.RANK))
        print("+++++")
    
    def ALL_print(self):
        self.RAW_print()
        self.FORMATED_print()
        self.TRIMMED_print()
        self.SORTED_print()
    
    
    def LINE_print(self):
        """
        if self.trimFailCount == 0:
            trimFailSTR = ""
        else:
            trimFailSTR = str(self.trimFailCount) +":"+ self.trimFail
        """
        
        if self.Failed_sort:
            failedSortSTR="Fa"
        else:
            failedSortSTR=""
        
        """
        pre_str="{}\t{}\t{}\t{}\t{}\t{:<22}".format(\
            self.ID, self.RANK, self.listing_FINAL, trimFailSTR, failedSortSTR, self.nimi[:22])
        """
        pre_str="{:<5}{:<5}{:>3}-{:<2}-{:<6}\t{:<22}".format(\
            self.ID, self.RANK, self.listing_FINAL, failedSortSTR, self.trimFail, self.nimi[:22])
        TL_karsinta_str="\t{}\t{}".format(\
            self.gearing, self.omavaraisuusaste)
        TL_sort_str="\t{}\t{}\t{}\t{}\t{}".format(\
            self.PB_kaytto, self.PE_kaytto, self.nykyinen_osinkotuotto_PROCENT,\
            self.ROE, self.osinkotuotto_keskiarvo_PROCENT)
        muut_str="\t\t{}\t{}\t{}".format(\
            self.toimiala_lyhenne, self.P_muutos_kerroin, self.toimialaluokka)
        
        print(pre_str + TL_karsinta_str + TL_sort_str + muut_str)
