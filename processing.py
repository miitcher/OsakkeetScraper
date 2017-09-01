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
        try:
            self.collection = self.collect_and_calculate_metrics()
            self.filter()
        except:
            logger.error("c_id: {}; c_name: {}".format(self.company_id,
                                                       self.company_name))
            traceback.print_exc()
            return "FAIL"
        return self.collection

    def get_tulostiedot_key(self):
        if self.metrics["kannattavuus"] is None:
            return None

        # YYYY
        year_str_0 = date.today().strftime("%Y")
        year_str_1 = str(int(year_str_0) - 1)
        year_str_2 = str(int(year_str_0) - 2)

        possible_keys = []
        for key in self.metrics["kannattavuus"]:
            possible_keys.append(key)

        for key in sorted(possible_keys, reverse=True):
            if key.startswith(year_str_0):
                return key
            elif key.startswith(year_str_1):
                return key
            elif key.startswith(year_str_2):
                return key

        logger.error(
            "Found no tulostiedot_key: c_id: {}; c_name: {}" \
            .format(self.company_id, self.company_name) \
            + "\n\tPossible keys: " + str(possible_keys)
        )
        return None

    def collect_and_calculate_metrics(self):
        collection = {}
        needs_tulostiedot_key = {} # Banks do not have these metrics.
        collection["tulostiedot_key"] = self.get_tulostiedot_key()

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

        if self.metrics["osingot"]:
            for top_key in self.metrics["osingot"]:
                osinko_dict = self.metrics["osingot"][top_key]
                osinko_year = str(osinko_dict["vuosi"])
                if osinko_year in osinko_tuotto_percent:
                    if osinko_dict["tuotto_%"]:
                        osinko_tuotto_percent[osinko_year] += osinko_dict["tuotto_%"]
                    if osinko_dict["oikaistu_euroina"]:
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

        """ Collect usefull metrics, that need the tulostiedot_key
        ROE_%
        nettotulos
        omavaraisuusaste_%
        gearing_%
        PB
        PE
        E
        P
        """
        if collection["tulostiedot_key"]:
            kannattavuus = self.metrics["kannattavuus"][collection["tulostiedot_key"]]
            needs_tulostiedot_key["ROE_%"]        = kannattavuus["oman_paaoman_tuotto_%"]
            needs_tulostiedot_key["nettotulos"] = kannattavuus["nettotulos"]

            vakavaraisuus = self.metrics["vakavaraisuus"][collection["tulostiedot_key"]]
            needs_tulostiedot_key["omavaraisuusaste_%"] = vakavaraisuus["omavaraisuusaste_%"]
            needs_tulostiedot_key["gearing_%"]          = vakavaraisuus["nettovelkaantumisaste_%"]

            sijoittajan_tunnuslukuja = self.metrics["sijoittajan_tunnuslukuja"][collection["tulostiedot_key"]]
            needs_tulostiedot_key["PB"] = sijoittajan_tunnuslukuja["p/b-luku"]
            needs_tulostiedot_key["PE"] = sijoittajan_tunnuslukuja["p/e-luku"]
            needs_tulostiedot_key["E"]  = sijoittajan_tunnuslukuja["tulos_(e)"]
            needs_tulostiedot_key["P"]  = sijoittajan_tunnuslukuja["markkina-arvo_(p)"]

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
        if collection["tulostiedot_key"] \
        and needs_tulostiedot_key["P"]:
            needs_tulostiedot_key["P_factor_fresh"] = round(
                collection["P_fresh"] / needs_tulostiedot_key["P"], 4
            )
            needs_tulostiedot_key["PB_fresh"] = round(
                needs_tulostiedot_key["P_factor_fresh"]
                * needs_tulostiedot_key["PB"], 2
            )
            needs_tulostiedot_key["PE_fresh"] = round(
                needs_tulostiedot_key["P_factor_fresh"]
                * needs_tulostiedot_key["PE"], 2
            )

        if needs_tulostiedot_key:
            collection["needs_tulostiedot_key"] = needs_tulostiedot_key
        else:
            collection["needs_tulostiedot_key"] = None

        return collection

    def _do_filtering(self, key, threshold_min=None, threshold_max=None):
        assert self.collection["tulostiedot_key"]
        val = self.collection["needs_tulostiedot_key"][key]
        if val is None:
            logger.debug("No {}: c_id: {}; c_name: {}" \
                         .format(key, self.company_id, self.company_name))
            self.passed_filter["skipped_filters"].append(key)
            return
        assert isinstance(val, float), \
            "key: {}, type: {}".format(key, type(val))
        passed = True
        if passed and threshold_min is not None \
        and val >= threshold_min:
            passed = False
        if passed and threshold_max is not None \
        and val <= threshold_max:
            passed = False
        self.passed_filter[key] = passed

    def filter(self):
        """
        When the collection is created, the collection metrics are compared
        towards the threshold, creating the self.passed_filter dictionary,
        that is added to the collection.

            Filtering:
        steady_osinko: osinkotuotto > 0% for five years
        gearing_% < 100%
            needs_tulostiedot_key
        omavaraisuusaste_% > 40%
            needs_tulostiedot_key
        ROE_% > 10%
            needs_tulostiedot_key
        steady_nettotulos: maximum 1 decreasing of nettotulos under five years
            needs_tulostiedot_key
        """
        self.passed_filter = {}
        self.passed_filter["skipped_filters"] = []
        self.passed_filter["steady_osinko"] = self.collection["steady_osinko"]

        if self.collection["tulostiedot_key"] is None:
            logger.debug("No tulostiedot_key: c_id: {}; c_name: {}" \
                         .format(self.company_id, self.company_name))
            self.passed_filter["skipped_filters"].extend([
                "gearing_%", "omavaraisuusaste_%", "ROE_%", "steady_nettotulos"
            ])
        else:
            self._do_filtering("gearing_%",             threshold_max=100)
            self._do_filtering("omavaraisuusaste_%",    threshold_min=40)
            self._do_filtering("ROE_%",                 threshold_min=10)

            # Put dictionary keys and values inside list as tuples,
            # so they can be sorted.
            nettotulos_list = [] # e.g. ("2016-12-01", 0.4)
            for key, val in self.metrics["kannattavuus"].items():
                nettotulos_list.append((key, val["nettotulos"]))

            decrease_count = 0
            years_from_now = 0
            last_nettotulos = None
            for key, nettotulos in sorted(nettotulos_list, key=lambda tup: tup[0]):
                assert isinstance(nettotulos, float), \
                    "nettotulos: {}".format(type(nettotulos))
                if last_nettotulos is not None:
                    if nettotulos < last_nettotulos:
                        decrease_count += 1
                last_nettotulos = nettotulos
                years_from_now += 1
                if years_from_now == 5:
                    break

            if decrease_count > 1:
                self.passed_filter["steady_nettotulos"] = False
            else:
                self.passed_filter["steady_nettotulos"] = True

        passed_all = True
        for pass_state in self.passed_filter.values():
            if not pass_state:
                passed_all = False
                break
        self.passed_filter["all"] = passed_all

        if not self.passed_filter["skipped_filters"]:
            self.passed_filter["skipped_filters"] = None

        self.collection["passed_filter"] = self.passed_filter


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
