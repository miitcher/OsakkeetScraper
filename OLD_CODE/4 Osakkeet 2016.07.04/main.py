import os
import sys
from PyQt5.QtWidgets import QApplication

from window import Window
from costum_conditions import Costum_conditions

from csv_save_and_load import YRITYKSIEN_TIEDOT_csv_file_WRITE, YRITYKSIEN_TIEDOT_csv_file_READ
from scrape_basic import scrape_ID_TO_NAME_DICT, scrape_YRITYS_OLIO_DICT



def manage_folders():
    #Creates a "Saved_data"-folder if one does not exist.
    if not os.path.isdir("Saved_data"):
        os.makedirs("Saved_data")
        print('"Saved_data" folder created')
    
    #Creates a "Settings"-folder if one does not exist.
    if not os.path.isdir("Settings"):
        os.makedirs("Settings")
        print('"Settings" folder created')

def safeAverageDivide(top, bot):
    try:
        avg = round(top / bot , 2)
    except ZeroDivisionError:
        avg = "-"
    return avg



class Kaytetaan():
    def __init__(self):
        self.ID_TO_NAME_DICT = {}
        self.YRITYS_OLIO_DICT = {}
        self.DATA_SET = False
        
        self.set_settings()
        
        self.sorted_yritys_olio_list = []
        
        self.Conditions = Costum_conditions()
    
    def set_settings(self):
        #POIKKEUKSET
        self.MISSING_TUNNUSLUKUJA_TABLE_TAG=[]
        self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG=[]
        self.MISSING_KURSSI_KUVAUS_YRITYKSESTA=[]
        
        #HANDPICKED
        self.osinkojako_5v_puuttuu_koska_listattu_hiljattain=[]
        self.huono_tunnusluku=[]
        self.laskevia_tuloksia=[]
        
        self.all_handpicked=[]
        
        
        filename = "Settings\\POIKKEUKSET_HANDPICKED.csv"
        f=open(filename, "r")
        
        for r in f:
            strs=r.strip().split(";")
            #print(strs)
            
            h=strs[0].strip()
            if h=="MISSING_TUNNUSLUKUJA_TABLE_TAG":
                l=self.MISSING_TUNNUSLUKUJA_TABLE_TAG
            elif h=="MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG":
                l=self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG
            elif h=="MISSING_KURSSI_KUVAUS_YRITYKSESTA":
                l=self.MISSING_KURSSI_KUVAUS_YRITYKSESTA
            
            elif h=="osinkojako_5v_puuttuu_koska_listattu_hiljattain":
                l=self.osinkojako_5v_puuttuu_koska_listattu_hiljattain
            elif h=="huono_tunnusluku":
                l=self.huono_tunnusluku
            elif h=="laskevia_tuloksia":
                l=self.laskevia_tuloksia
            
            else:
                continue
            
            c=0
            for i in strs:
                if c!=0:
                    try:
                        l.append(int(i))
                    except:
                        pass
                c+=1
        
        f.close()
        
        for i in self.osinkojako_5v_puuttuu_koska_listattu_hiljattain:
            self.all_handpicked.append(i)
        for i in self.huono_tunnusluku:
            self.all_handpicked.append(i)
        for i in self.laskevia_tuloksia:
            self.all_handpicked.append(i)
    
    
    def scrape_and_save(self):
        print("\nTIEDOT scraping from Kauppalehti.")
        self.ID_TO_NAME_DICT = scrape_ID_TO_NAME_DICT()
        self.YRITYS_OLIO_DICT = scrape_YRITYS_OLIO_DICT(self.ID_TO_NAME_DICT)
        print("TIEDOT scraped from Kauppalehti.")
        
        self.prosess_yritykset()
        self.Error_check_SCRAPE()
        
        YRITYKSIEN_TIEDOT_csv_file_WRITE(self.YRITYS_OLIO_DICT)
    
    def load(self, filename):
        self.YRITYS_OLIO_DICT = YRITYKSIEN_TIEDOT_csv_file_READ(filename)
        print("\nTIEDOT has been loaded from the file: {}".format(filename))
        
        self.prosess_yritykset()
        self.Error_check_LOAD()
    
    def companies_print(self):
        if self.DATA_SET:
            self.APPEND_COSTUM_IN_sorted_yritys_olio_list()
            self.SORT_sorted_yritys_olio_list()
            
            self.companies_header_print()
            
            descriptive_str =   "ID\tRank\tLF\tTFC:WFT\tFS\tName\t\t\t"+\
                                "Gearing\tOVA\t"+\
                                "P/B\tP/E\tOT\tROE\t"+\
                                "Toimia.\tP_ker.\tToimialaluokka"
            
            print(descriptive_str)
            
            for yritys in self.sorted_yritys_olio_list:
                yritys.LINE_print()
            
            print(descriptive_str)
            
            self.set_averages_FOR_sorted_yritys_olio_list()
            print("\t"*6 + "AVERAGES:\t{}\t{}\t{}\t{}\t{}\t{}".format(\
                self.gearing_avg, self.OVA_avg, self.PB_avg, self.PE_avg, self.OT_avg, self.ROE_avg))
        else:
            print("The DATA is not set!")
    
    
    def prosess_yritykset(self):
        for ID in self.YRITYS_OLIO_DICT:
            self.YRITYS_OLIO_DICT[ID].prosess()
        self.DATA_SET = True
        
        for ID in self.YRITYS_OLIO_DICT:
            self.sorted_yritys_olio_list.append(self.YRITYS_OLIO_DICT[ID])
        self.SORT_sorted_yritys_olio_list()
        
        print("Companies prosessed. (format, validate, trim, sort)")
        
        print("\tvalidate NOT READY!")
        
        """
        self.All_ERROR_list_print()
        print("\nTest Error Check")
        print("MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG")
        print("POP: ", self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG.pop())
        self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG.append(1901)
        print("APPEND: 1901")
        """
    
    def APPEND_COSTUM_IN_sorted_yritys_olio_list(self):
        if not self.Conditions.Checkbox_conditions_set:
            print("\nCheckbox conditions are not set!")
            return
        
        if not self.Conditions.Threshold_conditions_set:
            print("\nThreshold conditions are not set!")
            return
        
        self.sorted_yritys_olio_list=[]
        con = self.Conditions
        
        for ID in self.YRITYS_OLIO_DICT:
            
            y   = self.YRITYS_OLIO_DICT[ID]
            
            if not (y.ID in self.all_handpicked and con.ShowHandpicked):
                if y.KARSINTA_LAPI:
                    if not con.ShowPassedTrim:
                        continue
                else:
                    if not y.KAR_gearing and not con.ShowGearingFail:
                        continue
                    if not y.KAR_omavaraisuusaste and not con.ShowOVAFail:
                        continue
                    if not y.KAR_ROE and not con.ShowROEFail:
                        continue
                    if not y.KAR_viisi_vuotta_osinkoa and not con.ShowViisiOsinkoaFail:
                        continue
                    if not y.KAR_tulokset_nousee_viisi_vuotta and not con.ShowTulosNousuFail:
                        continue
            
            
            if y.Failed_sort:
                if not con.ShowFailedSort:
                    continue
            else:
                if not con.ShowPassedSort:
                    continue
            
            
            listaToimialoista=["Kulutuspalvelut","Kulutustavarat","Perusteollisuus","Rahoitus",\
                               "Teknologia","Teollisuustuotteet ja -palvelut","Terveydenhuolto",\
                               "Tietoliikennepalvelut","Yleishyodylliset palvelut","Oljy ja kaasu"]
            
            if y.toimiala == listaToimialoista[0] and not con.ShowTaKuPa:
                continue
            elif y.toimiala == listaToimialoista[1] and not con.ShowTaKuTa:
                continue
            elif y.toimiala == listaToimialoista[2] and not con.ShowTaPeTe:
                continue
            elif y.toimiala == listaToimialoista[3] and not con.ShowTaRaho:
                continue
            elif y.toimiala == listaToimialoista[4] and not con.ShowTaTekn:
                continue
            elif y.toimiala == listaToimialoista[5] and not con.ShowTaTePa:
                continue
            elif y.toimiala == listaToimialoista[6] and not con.ShowTaTeHu:
                continue
            elif y.toimiala == listaToimialoista[7] and not con.ShowTaTiLiPa:
                continue
            elif y.toimiala == listaToimialoista[8] and not con.ShowTaYlPa:
                continue
            elif y.toimiala == listaToimialoista[9] and not con.ShowTaOlKa:
                continue
            elif not y.toimiala in listaToimialoista:
                print("HUOM: Outo toimiala: [{}]!".format(y.toimiala))
            
            
            if y.gearing:
                if y.gearing > con.CTGearing:
                    continue
            if y.omavaraisuusaste:
                if y.omavaraisuusaste < con.CTOVA:
                    continue
            if y.PB_kaytto:
                if y.PB_kaytto > con.CTPB:
                    continue
            if y.PE_kaytto:
                if y.PE_kaytto > con.CTPE:
                    continue
            if y.nykyinen_osinkotuotto_PROCENT:
                if y.nykyinen_osinkotuotto_PROCENT < con.CTOT:
                    continue
            if y.ROE:
                if y.ROE < con.CTROE:
                    continue
            
            
            self.sorted_yritys_olio_list.append(self.YRITYS_OLIO_DICT[ID])
    
    def SORT_sorted_yritys_olio_list(self):
        """YRITYS-OLIOT SAAVAT KAR-TUNNUSLUVUT
        yritys.PB_listing
        yritys.PE_listing
        yritys.osinkotuotto_listing
        yritys.ROE_listing
        
        yritys.listing_FINAL
        yritys.RANK
        yritys.Failed_sort
        """
        
        MAX_listing = len(self.sorted_yritys_olio_list) +1
        Failed_sort_number = MAX_listing
        
        #P/B matala
        self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.PB_kaytto)
        c=1
        for yritys in self.sorted_yritys_olio_list:
            if yritys.PB_kaytto >0:
                yritys.PB_listing = c
                c+=1
            else:
                yritys.PB_listing = Failed_sort_number
                yritys.Failed_sort = True
        
        #P/E matala
        self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.PE_kaytto)
        c=1
        for yritys in self.sorted_yritys_olio_list:
            if yritys.PE_kaytto >0:
                yritys.PE_listing = c
                c+=1
            else:
                yritys.PE_listing = Failed_sort_number
                yritys.Failed_sort = True
        
        #OSINKOTUOTTO korkea
        self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.nykyinen_osinkotuotto_PROCENT, reverse=True)
        c=1
        for yritys in self.sorted_yritys_olio_list:
            if yritys.nykyinen_osinkotuotto_PROCENT >0:
                yritys.osinkotuotto_listing = c
                c+=1
            else:
                yritys.osinkotuotto_listing = Failed_sort_number
                yritys.Failed_sort = True
        
        #ROE korkea and Listing SUM
        self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.ROE, reverse=True)
        c=1
        for yritys in self.sorted_yritys_olio_list:
            if yritys.ROE >0:
                yritys.ROE_listing = c
                c+=1
            else:
                yritys.ROE_listing = Failed_sort_number
                yritys.Failed_sort = True
            
            yritys.listing_FINAL = yritys.PB_listing+yritys.PE_listing+yritys.osinkotuotto_listing+yritys.ROE_listing
        
        #SORT by listing_FINAL and RANK
        self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.listing_FINAL)
        c=1
        for yritys in self.sorted_yritys_olio_list:
            yritys.RANK = c
            c+=1
    
    
    def companies_header_print(self):
        print("\n\tINFO about Companies in YRITYS_OLIO_DICT")
        print("LF=Listing Final; TFC=Trim Fail Count; WFT=What Failed in Trim; FS=Failed Sort; OVA=Omavaraisuusaste; OT=Osinkotuotto-%")
        print("What failed in TRIM: H=HANDPICKED; G=gearing; O=omavaraisuusaste; R=ROE; J=jaettu viisi vuotta osinkoa; T=tulokset nousee viisi vuotta")
        print("Toimialat:\tKuPa=Kulutuspalvelut; KuTa=Kulutustavarat; PeTe=Perusteollisuus; Raho=Rahoitus;")
        print("\t\tTekn=Teknologia; TePa=Teollisuustuotteet ja -palvelut; TeHu=Terveydenhuolto;")
        print("\t\tTiLiPa=Tietoliikennepalvelut; YlPa=Yleishyodylliset palvelut; OlKa=Oljy ja kaasu")
        
        if self.Conditions.Threshold_conditions_set:
            print("\n"+"\t"*5 + "Costum threasholds:\t<{}\t>{}\t<{}\t<{}\t>{}\t>{}"\
                  .format(self.Conditions.CTGearing, self.Conditions.CTOVA, self.Conditions.CTPB,\
                          self.Conditions.CTPE, self.Conditions.CTOT, self.Conditions.CTROE))
        
        print("\t"*5 +  "Prefered (sort):\t\t\tLow\tLow\tHigh\tHigh")
        print("\t"*5 +  "Trimm threasholds:\t<100\t>40\t\t\t\t>10")
    
    def set_averages_FOR_sorted_yritys_olio_list(self):
        
        gearing_sum = 0
        gearing_c = 0
        OVA_sum = 0
        OVA_c = 0
        PB_sum = 0
        PB_c = 0
        PE_sum = 0
        PE_c = 0
        OT_sum = 0
        OT_c = 0
        ROE_sum = 0
        ROE_c = 0
        
        for y in self.sorted_yritys_olio_list:
            if type(y.gearing)==float:
                gearing_sum += y.gearing
                gearing_c +=1
            if type(y.omavaraisuusaste)==float:
                OVA_sum += y.omavaraisuusaste
                OVA_c +=1
            if type(y.PB_kaytto)==float:
                PB_sum += y.PB_kaytto
                PB_c +=1
            if type(y.PE_kaytto)==float:
                PE_sum += y.PE_kaytto
                PE_c +=1
            if type(y.nykyinen_osinkotuotto_PROCENT)==float:
                OT_sum += y.nykyinen_osinkotuotto_PROCENT
                OT_c +=1
            if type(y.ROE)==float:
                ROE_sum += y.ROE
                ROE_c +=1
        
        self.gearing_avg =  safeAverageDivide(gearing_sum, gearing_c)
        self.OVA_avg =      safeAverageDivide(OVA_sum, OVA_c)
        self.PB_avg =       safeAverageDivide(PB_sum, PB_c)
        self.PE_avg =       safeAverageDivide(PE_sum, PE_c)
        self.OT_avg =       safeAverageDivide(OT_sum, OT_c)
        self.ROE_avg =      safeAverageDivide(ROE_sum, ROE_c)
    
    
    def Error_check_SCRAPE(self):
        self.Unexpected_ERROR_list_print()
        self.Expected_ERRORS_list_print_SCRAPE()
    
    def Error_check_LOAD(self):
        self.Unexpected_ERROR_list_print()
        self.Expected_ERRORS_list_print_LOAD()
    
    def All_ERROR_list_print(self):
        print("\n\tALL ERRORS:")
        print("MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:\n", self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG)
        print("MISSING_TUNNUSLUKUJA_TABLE_TAG:\n", self.MISSING_TUNNUSLUKUJA_TABLE_TAG)
        print("MISSING_KURSSI_KUVAUS_YRITYKSESTA:\n", self.MISSING_KURSSI_KUVAUS_YRITYKSESTA, "\n")
        
        Error_count = 0
        Yritys_count = 0
        
        for ID in self.YRITYS_OLIO_DICT:
            E_list = self.YRITYS_OLIO_DICT[ID].ERROR_list
            
            if len(E_list) > 0:
                print("{} All Errors:".format(ID))
                Yritys_count += 1
                for e in E_list:
                    print("\t" + e)
                    Error_count += 1
            
        if Error_count > 0:
            print("\nAll Errors:")
            print("\tCompanies with Errors:\t{}".format(Yritys_count))
            print("\tErrors Sum:\t\t{}".format(Error_count))
        else:
            print("None")
    
    def Unexpected_ERROR_list_print(self):
        print("\n\tUNEXPECTED ERRORS:")
        
        Error_count = 0
        Yritys_count = 0
        
        for ID in self.YRITYS_OLIO_DICT:
            E_list = self.YRITYS_OLIO_DICT[ID].ERROR_list
            
            Unexpected_E_list = []
            if len(E_list) > 0:
                for e in E_list:
                    strs=e.split()
                    
                    
                    if strs[0] == "FormatError:":
                        
                        if strs[1] == "toiminnan_laajuus_mat" or \
                           strs[1] == "kannattavuus_mat" or \
                           strs[1] == "vakavaraisuus_mat" or \
                           strs[1] == "maksuvalmius_mat" or \
                           strs[1] == "sijoittajan_tunnuslukuja_mat":
                            if ID in self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:
                                continue
                    
                    
                    elif strs[0] == "ScrapeError:":
                        
                        if strs[1] == "toiminnan_laajuus_mat" or \
                           strs[1] == "kannattavuus_mat" or \
                           strs[1] == "vakavaraisuus_mat" or \
                           strs[1] == "maksuvalmius_mat" or \
                           strs[1] == "sijoittajan_tunnuslukuja_mat":
                            if ID in self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:
                                continue
                        
                        elif strs[1] == "tunnuslukuja_dict":
                            if ID in self.MISSING_TUNNUSLUKUJA_TABLE_TAG:
                                continue
                        
                        elif strs[1] == "kuvaus_yrityksesta":
                            if ID in self.MISSING_KURSSI_KUVAUS_YRITYKSESTA:
                                continue
                    
                    
                    Unexpected_E_list.append(e)
            
            if len(Unexpected_E_list) > 0:
                print("{} Unexpected Errors:".format(ID))
                Yritys_count += 1
                for e in Unexpected_E_list:
                    print("\t" + e)
                    Error_count += 1
        
        if Error_count > 0:
            print("\nMISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:\n", self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG)
            print("MISSING_TUNNUSLUKUJA_TABLE_TAG:\n", self.MISSING_TUNNUSLUKUJA_TABLE_TAG)
            print("MISSING_KURSSI_KUVAUS_YRITYKSESTA:\n", self.MISSING_KURSSI_KUVAUS_YRITYKSESTA)
            
            print("\nUnexpected Errors:")
            print("\tCompanies with Errors:\t{}".format(Yritys_count))
            print("\tErrors Sum:\t\t{}".format(Error_count))
        else:
            print("None")
    
    def Expected_ERRORS_list_print_SCRAPE(self):
        print("\n\tEXPECTED ERRORS THAT DID NOT OCCUR:")
        
        Unoccured_Error_count = 0
        Yritys_count = 0
        
        for ID in self.YRITYS_OLIO_DICT:
            E_list = self.YRITYS_OLIO_DICT[ID].ERROR_list
            
            
            """ EXPECTED ERRORS
            MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG; Expected Errors:
                FormatError:
                    kannattavuus_mat
                    vakavaraisuus_mat
                    sijoittajan_tunnuslukuja_mat
                ScrapeError:
                    toiminnan_laajuus_mat
                    kannattavuus_mat
                    vakavaraisuus_mat
                    maksuvalmius_mat
                    sijoittajan_tunnuslukuja_mat
            
            MISSING_TUNNUSLUKUJA_TABLE_TAG; Expected Errors:
                ScrapeError:
                    tunnuslukuja_dict
            
            MISSING_KURSSI_KUVAUS_YRITYKSESTA; Expected Errors:
                ScrapeError:
                    kuvaus_yrityksesta
            """
            
            EEOdict = {}    # EEO = Expected Errors Occured
            
            if ID in self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:
                EEOdict["FormatError: kannattavuus_mat"] = False
                EEOdict["FormatError: vakavaraisuus_mat"] = False
                EEOdict["FormatError: sijoittajan_tunnuslukuja_mat"] = False
                
                EEOdict["ScrapeError: toiminnan_laajuus_mat"] = False
                EEOdict["ScrapeError: kannattavuus_mat"] = False
                EEOdict["ScrapeError: vakavaraisuus_mat"] = False
                EEOdict["ScrapeError: maksuvalmius_mat"] = False
                EEOdict["ScrapeError: sijoittajan_tunnuslukuja_mat"] = False
            
            if ID in self.MISSING_TUNNUSLUKUJA_TABLE_TAG:
                EEOdict["ScrapeError: tunnuslukuja_dict"] = False
            
            if ID in self.MISSING_KURSSI_KUVAUS_YRITYKSESTA:
                EEOdict["ScrapeError: kuvaus_yrityksesta"] = False
            
            
            Unoccured_Errors_for_company = False
            for e in EEOdict:
                if e in E_list:
                    EEOdict[e]=True
                else:
                    Unoccured_Errors_for_company = True
            
            if Unoccured_Errors_for_company:
                print("{} Expected Errors that did not occur:".format(ID))
                Yritys_count += 1
                for e in EEOdict:
                    if not EEOdict[e]:
                        print("\t" + e)
                        Unoccured_Error_count += 1
        
        if Unoccured_Error_count > 0:
            print("\nMISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:\n", self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG)
            print("MISSING_TUNNUSLUKUJA_TABLE_TAG:\n", self.MISSING_TUNNUSLUKUJA_TABLE_TAG)
            print("MISSING_KURSSI_KUVAUS_YRITYKSESTA:\n", self.MISSING_KURSSI_KUVAUS_YRITYKSESTA)
            
            print("\nExpected Errors that did not occur:")
            print("\tCompanies with Expected Errors, not occuring:\t{}".format(Yritys_count))
            print("\tExpected Errors, not occuring Sum:\t\t{}".format(Unoccured_Error_count))
        else:
            print("None")
    
    def Expected_ERRORS_list_print_LOAD(self):
        print("\n\tEXPECTED ERRORS THAT DID NOT OCCUR:")
        
        Unoccured_Error_count = 0
        Yritys_count = 0
        
        for ID in self.YRITYS_OLIO_DICT:
            E_list = self.YRITYS_OLIO_DICT[ID].ERROR_list
            
            
            """ EXPECTED ERRORS
            MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG; Expected Errors:
                FormatError:
                    kannattavuus_mat
                    vakavaraisuus_mat
                    sijoittajan_tunnuslukuja_mat
            """
            
            EEOdict = {}    # EEO = Expected Errors Occured
            
            if ID in self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:
                EEOdict["FormatError: kannattavuus_mat"] = False
                EEOdict["FormatError: vakavaraisuus_mat"] = False
                EEOdict["FormatError: sijoittajan_tunnuslukuja_mat"] = False
            
            
            Unoccured_Errors_for_company = False
            for e in EEOdict:
                if e in E_list:
                    EEOdict[e]=True
                else:
                    Unoccured_Errors_for_company = True
            
            
            if Unoccured_Errors_for_company:
                print("{} Expected Errors that did not occur:".format(ID))
                Yritys_count += 1
                for e in EEOdict:
                    if not EEOdict[e]:
                        print("\t" + e)
                        Unoccured_Error_count += 1
        
        if Unoccured_Error_count > 0:
            print("\nMISSING_KURSSI_TULOSTIEDOT_TABLE_TAG:\n", self.MISSING_KURSSI_TULOSTIEDOT_TABLE_TAG)
            
            print("\nExpected Errors that did not occur:")
            print("\tCompanies with Expected Errors, not occuring:\t{}".format(Yritys_count))
            print("\tExpected Errors, not occuring Sum:\t\t{}".format(Unoccured_Error_count))
        else:
            print("None")



if __name__ == '__main__':
    manage_folders()
    kaytetaan = Kaytetaan()
    
    app = QApplication(sys.argv)
    Window = Window(kaytetaan)
    Window.show()
    sys.exit(app.exec_())