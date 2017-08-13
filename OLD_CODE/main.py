from costum_conditions import Costum_conditions


class Kaytetaan():
    def __init__(self):
        self.Conditions = Costum_conditions()

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
