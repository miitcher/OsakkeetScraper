import logging, traceback
from datetime import date


logger = logging.getLogger('root')


class ProcessorException(Exception):
    pass

class RankerException(Exception):
    pass


class Processor():
    def __init__(self, metrics):
        # Takes one company metrics as input, and returns a filtered collection.
        assert isinstance(metrics, dict) and len(metrics) > 10

        self.metrics = metrics
        self.company_id = self.metrics["company_id"]
        self.company_name = self.metrics["company_name"]

        assert self.company_id
        assert isinstance(self.company_id, int)
        assert isinstance(self.company_name, str)

    def process(self):
        self.collection = self.collect_and_calculate_metrics()
        #self.filter()
        return self.collection

    def get_tulostiedot_key(self):
        # TODO: Could be more more readable.
        try:
            # "12/16", used for dictionaries scraped from the tulostiedot-page
            tulostiedot_key = None
            current_year = int(date.today().strftime("%y")) # YY
            key_dict = {} # keys_dict(year_int) = key_str
            for key in self.metrics["kannattavuus"]:
                if key.endswith("/{}".format(current_year)) or \
                   key.endswith("/{}".format(current_year - 1)):
                    parts = key.split("/")
                    key_dict[int(parts[1])] = key
            if current_year in key_dict:
                tulostiedot_key = key_dict[current_year]
            elif (current_year - 1) in key_dict:
                tulostiedot_key = key_dict[(current_year - 1)]
            else:
                all_keys = []
                for key in self.metrics["kannattavuus"]:
                    all_keys.append(key)
                raise ProcessorException("Unexpected keys: {}".format(str(all_keys)))
            assert tulostiedot_key
            assert tulostiedot_key == "12/16" # Changed when time passes
            return tulostiedot_key
        except:
            traceback.print_exc()
            return None

    def collect_and_calculate_metrics(self):
        collection = {}

        """ Collect current osinko metrics and check steady osinko
        osinko_tuotto_%
        osinko_euro
        steady_osinko    : osinkotuotto > 0% for five years
        """
        current_year = int(date.today().strftime("%Y")) # YYYY
        osinko_tuotto_percent = {}
        osinko_euro = {}
        for year in range(current_year-4, current_year+1):
            osinko_tuotto_percent[str(year)] = 0
            osinko_euro[str(year)] = 0

        for top_key in self.metrics["osingot"]:
            osinko_dict = self.metrics["osingot"][top_key]
            osinko_year = str(osinko_dict["vuosi"])
            if osinko_year in osinko_tuotto_percent:
                osinko_tuotto_percent[osinko_year] += osinko_dict["tuotto_%"]
                osinko_euro[osinko_year] += osinko_dict["oikaistu_euroina"]

        steady_osinko = True
        for year in osinko_tuotto_percent:
            if osinko_tuotto_percent[year] <= 0:
                steady_osinko = False
                break

        collection["osinko_tuotto_%"] = osinko_tuotto_percent
        collection["osinko_euro"] = osinko_euro
        collection["steady_osinko"] = steady_osinko

        """ Collect usefull metrics
        company_id
        company_name
        kurssi
        kuvaus
        scrape_date
        toimiala
        toimialaluokka
        osakkeet_kpl
        markkina_arvo  TODO: Added, but is it needed?
        """
        collection["company_id"]       = self.metrics["company_id"]
        collection["company_name"]     = self.metrics["company_name"]
        collection["kurssi"]           = self.metrics["kurssi"]
        collection["kuvaus"]           = self.metrics["kuvaus"]
        collection["scrape_date"]      = self.metrics["scrape_date"]

        perustiedot = self.metrics["perustiedot"]
        collection["toimiala"]         = perustiedot["toimiala"]
        collection["toimialaluokka"]   = perustiedot["toimialaluokka"]
        collection["osakkeet_kpl"]     = perustiedot["osakkeet_kpl"]
        collection["markkina_arvo"]    = perustiedot["markkina_arvo"]

        """ Collect usefull metrics, that need the tulostiedot_key
        tulostiedot_key
        ROE
        nettotulos
        omavaraisuusaste
        gearing
        PB
        PE
        E
        P
        """
        tulostiedot_key = self.get_tulostiedot_key() # "12/16"
        collection["tulostiedot_key"] = tulostiedot_key
        if tulostiedot_key:
            kannattavuus = self.metrics["kannattavuus"][tulostiedot_key]
            collection["ROE"]        = kannattavuus["oman_paaoman_tuotto_%"]
            collection["nettotulos"] = kannattavuus["nettotulos"]

            vakavaraisuus = self.metrics["vakavaraisuus"][tulostiedot_key]
            collection["omavaraisuusaste"] = vakavaraisuus["omavaraisuusaste, %"]
            collection["gearing"]          = vakavaraisuus["nettovelkaantumisaste, %"]

            sijoittajan_tunnuslukuja = self.metrics["sijoittajan_tunnuslukuja"][tulostiedot_key]
            collection["PB"] = sijoittajan_tunnuslukuja["p/b-luku"]
            collection["PE"] = sijoittajan_tunnuslukuja["p/e-luku"]
            collection["E"]  = sijoittajan_tunnuslukuja["tulos (e)"]
            collection["P"]  = sijoittajan_tunnuslukuja["markkina-arvo (p)"]

        """ Calculate fresh metrics, with current stock price
        osinko_tuotto_%_fresh
        P_fresh
        P_factor_fresh
        PB_fresh
        PE_fresh
        """
        current_year_str = date.today().strftime("%Y") # "YYYY"
        collection["osinko_tuotto_%_fresh"] = round(
            100 * collection["osinko_euro"][current_year_str]
            / collection["kurssi"], 2
        )
        collection["P_fresh"] = round(
            collection["osakkeet_kpl"]
            * collection["kurssi"] / 1e6, 4
        )
        if tulostiedot_key:
            collection["P_factor_fresh"] = round(
                collection["P_fresh"] / collection["P"], 4
            )
            collection["PB_fresh"] = round(
                collection["P_factor_fresh"] * collection["PB"], 2
            )
            collection["PE_fresh"] = round(
                collection["P_factor_fresh"] * collection["PE"], 2
            )

        return collection

    def filter(self): # OLD: trim
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
        
        
        #RAHOITUSRAKENNE (gearing <100%, omavaraisuusaste >40%)
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
        
        #TUOTTO (ROE >10%)
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


class Ranker(): # OLD: Kaytetaan
    def __init__(self, collection_list):
        # Takes multiple companies collection as input.
        self.Conditions = None

    def companies_print(self):
        if self.DATA_SET:
            self.APPEND_COSTUM_IN_sorted_yritys_olio_list()
            self.SORT_sorted_yritys_olio_list()
            
            self.companies_header_print()
            
            descriptive_str =   "ID   Rank LiF-SF-TF    \tName\t\t\t"+\
                                "Gearing\tOVA\t"+\
                                "P/B\tP/E\tOT\tROE\t"+\
                                "OT ka5\t\t"+\
                                "Toimia.\tP_ker.\tToimialaluokka"
            
            print(descriptive_str)
            
            for yritys in self.sorted_yritys_olio_list:
                yritys.LINE_print()
            
            print(descriptive_str)
            
            self.set_averages_FOR_sorted_yritys_olio_list()
            print("\t"*4 + "AVERAGES:\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(\
                self.gearing_avg, self.OVA_avg, self.PB_avg, self.PE_avg, self.OT_avg, self.ROE_avg, self.OT_ka_avg))
        else:
            print("The DATA is not set!")

    def APPEND_COSTUM_IN_sorted_yritys_olio_list(self):
        if not self.Conditions.set_Show_CB_conditions:
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
            if y.osinkotuotto_keskiarvo_PROCENT:
                if y.osinkotuotto_keskiarvo_PROCENT < con.CTOTKA:
                    continue
            
            
            self.sorted_yritys_olio_list.append(self.YRITYS_OLIO_DICT[ID])

    def SORT_sorted_yritys_olio_list(self):
        """YRITYS-OLIOT SAAVAT KAR-TUNNUSLUVUT
        yritys.Gearing_listing
        yritys.OVA_listing
        yritys.PB_listing
        yritys.PE_listing
        yritys.OT_listing
        yritys.ROE_listing
        yritys.OT_ka_listing
        
        yritys.listing_FINAL
        yritys.RANK
        yritys.Failed_sort
        """
        
        MAX_listing = len(self.sorted_yritys_olio_list) +1
        Failed_sort_number = MAX_listing
        
        con = self.Conditions
        
        
        #Gearing matala
        if con.SBgearing:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.gearing)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.gearing:
                    yritys.Gearing_listing = c
                    c+=1
                else:
                    yritys.Gearing_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.Gearing_listing = 0
        
        #Omavaraisuusaste korkea
        if con.SBova:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.omavaraisuusaste, reverse=True)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.omavaraisuusaste:
                    yritys.OVA_listing = c
                    c+=1
                else:
                    yritys.OVA_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.OVA_listing = 0
        
        #P/B matala
        if con.SBpb:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.PB_kaytto)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.PB_kaytto >0:
                    yritys.PB_listing = c
                    c+=1
                else:
                    yritys.PB_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.PB_listing = 0
        
        #P/E matala
        if con.SBpe:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.PE_kaytto)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.PE_kaytto >0:
                    yritys.PE_listing = c
                    c+=1
                else:
                    yritys.PE_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.PE_listing = 0
        
        #Osinkotuotto korkea
        if con.SBot:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.nykyinen_osinkotuotto_PROCENT, reverse=True)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.nykyinen_osinkotuotto_PROCENT >0:
                    yritys.OT_listing = c
                    c+=1
                else:
                    yritys.OT_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.OT_listing = 0
        
        #ROE korkea
        if con.SBroe:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.ROE, reverse=True)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.ROE >0:
                    yritys.ROE_listing = c
                    c+=1
                else:
                    yritys.ROE_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.ROE_listing = 0
        
        #Osinkotuotto keskiarvo 5v korkea
        if con.SBotka:
            self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.osinkotuotto_keskiarvo_PROCENT, reverse=True)
            c=1
            for yritys in self.sorted_yritys_olio_list:
                if yritys.osinkotuotto_keskiarvo_PROCENT >0:
                    yritys.OT_ka_listing = c
                    c+=1
                else:
                    yritys.OT_ka_listing = Failed_sort_number
                    yritys.Failed_sort = True
        else:
            for y in self.sorted_yritys_olio_list:
                y.OT_ka_listing = 0
        
        
        #Listing SUM
        for y in self.sorted_yritys_olio_list:
            y.listing_FINAL = y.Gearing_listing +y.OVA_listing +y.PB_listing +\
                    y.PE_listing +y.OT_listing +y.ROE_listing +y.OT_ka_listing
        
        #RANK
        self.sorted_yritys_olio_list = sorted(self.sorted_yritys_olio_list, key=lambda yritys: yritys.listing_FINAL)
        c=1
        for yritys in self.sorted_yritys_olio_list:
            yritys.RANK = c
            c+=1

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
        OT_ka_sum = 0
        OT_ka_c = 0
        
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
            if type(y.osinkotuotto_keskiarvo_PROCENT)==float:
                OT_ka_sum += y.osinkotuotto_keskiarvo_PROCENT
                OT_ka_c +=1
        
        self.gearing_avg =  safeAverageDivide(gearing_sum, gearing_c)
        self.OVA_avg =      safeAverageDivide(OVA_sum, OVA_c)
        self.PB_avg =       safeAverageDivide(PB_sum, PB_c)
        self.PE_avg =       safeAverageDivide(PE_sum, PE_c)
        self.OT_avg =       safeAverageDivide(OT_sum, OT_c)
        self.ROE_avg =      safeAverageDivide(ROE_sum, ROE_c)
        self.OT_ka_avg =       safeAverageDivide(OT_ka_sum, OT_ka_c)


def safeAverageDivide(top, bot):
    try:
        avg = round(top / bot , 2)
    except ZeroDivisionError:
        avg = "-"
    return avg
