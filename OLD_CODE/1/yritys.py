

class Yritys():

    
    def karsi(self):
        #RAHOITUSRAKENNE (gearing <100%, omavaraisuusaste >40%)
        if self.gearing:
            if self.gearing <100:
                self.KAR_gearing=True
            else:
                self.KAR_gearing=False
        else:
            self.KAR_gearing=False
        
        if self.omavaraisuusaste:
            if self.omavaraisuusaste >40:
                self.KAR_omavaraisuusaste=True
            else:
                self.KAR_omavaraisuusaste=False
        else:
            self.KAR_omavaraisuusaste=False
        
        #TUOTTO (ROE >10%)
        if self.ROE:
            if self.ROE >10:
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
    
    def karsinta_print(self):
        print("\n+++++KARSINTA TIEDOT:")
        print("KAR_gearing\t\t{}".format(self.KAR_gearing))
        print("KAR_omavaraisuusaste\t{}".format(self.KAR_omavaraisuusaste))
        print("KAR_ROE\t\t\t{}".format(self.KAR_ROE))
        print("KAR_5v._osinkoa\t\t{}".format(self.KAR_viisi_vuotta_osinkoa))
        print("KAR_tulokset_nousee_5v.\t{}".format(self.KAR_tulokset_nousee_viisi_vuotta))
        
        print("\nKARSINTA_LAPI\t\t{}".format(self.KARSINTA_LAPI))
        print("+++++\n")
    
    def set_listing_FINAL(self):
        summa=self.PB_listing+self.PE_listing+self.osinkotuotto_listing+self.ROE_listing
        self.listing_FINAL = summa
    
    def sort_print(self):
        print("\n+++++SORT TIEDOT:")
        print("\t\tLISTING\tTUNNUSLUKU")
        print("P/B\t\t{}\t{}".format(self.PB_listing, self.nykyinen_PB_luku))
        print("P/E\t\t{}\t{}".format(self.PE_listing, self.nykyinen_PE_luku))
        print("Osinkot.\t{}\t{} %".format(self.osinkotuotto_listing, self.nykyinen_osinkotuotto_PROCENT))
        print("ROE\t\t{}\t{}".format(self.ROE_listing, self.ROE))
        print("Listing_FINAL\t{}".format(self.listing_FINAL))
        print("+++++\n")
    
    