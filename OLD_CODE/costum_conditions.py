class Costum_conditions():
    def __init__(self):
        self.Threshold_conditions_set = False
        self.Show_CB_conditions_set  = False
        self.Sort_CB_conditions_set  = False
    
    def set_Threshold_conditions(self, \
            CTGearing, CTOVA, CTPB, CTPE, CTOT, CTROE, CTOTKA):
        
        self.CTGearing = CTGearing
        self.CTOVA = CTOVA
        self.CTPB = CTPB
        self.CTPE = CTPE
        self.CTOT = CTOT
        self.CTROE = CTROE
        self.CTOTKA = CTOTKA
        
        
        self.Threshold_conditions_set = True
    
    def set_Show_CB_conditions(self, \
            ShowGearingFail, ShowOVAFail, ShowROEFail, ShowViisiOsinkoaFail, \
            ShowTulosNousuFail, ShowPassedTrim, ShowHandpicked, \
            ShowTaKuPa, ShowTaKuTa, ShowTaPeTe, ShowTaRaho, ShowTaTekn, ShowTaTePa, \
            ShowTaTeHu, ShowTaTiLiPa, ShowTaYlPa, ShowTaOlKa, ShowTaUnknown, \
            ShowFailedSort, ShowPassedSort):
        
        
        self.ShowGearingFail = ShowGearingFail
        self.ShowOVAFail = ShowOVAFail
        self.ShowROEFail = ShowROEFail
        self.ShowViisiOsinkoaFail = ShowViisiOsinkoaFail
        
        self.ShowTulosNousuFail = ShowTulosNousuFail
        self.ShowPassedTrim = ShowPassedTrim
        self.ShowHandpicked = ShowHandpicked
        
        
        self.ShowTaKuPa = ShowTaKuPa
        self.ShowTaKuTa = ShowTaKuTa
        self.ShowTaPeTe = ShowTaPeTe
        self.ShowTaRaho = ShowTaRaho
        self.ShowTaTekn = ShowTaTekn
        self.ShowTaTePa = ShowTaTePa
        
        self.ShowTaTeHu = ShowTaTeHu
        self.ShowTaTiLiPa = ShowTaTiLiPa
        self.ShowTaYlPa = ShowTaYlPa
        self.ShowTaOlKa = ShowTaOlKa
        self.ShowTaUnknown = ShowTaUnknown
        
        
        self.ShowFailedSort = ShowFailedSort
        self.ShowPassedSort = ShowPassedSort
        
        
        
        self.Show_CB_conditions_set = True
    
    def set_Sort_CB_conditions(self, \
            SBgearing, SBova, SBpb, SBpe, SBot, SBroe, SBotka):
        
        self.SBgearing=SBgearing
        self.SBova=SBova
        self.SBpb=SBpb
        self.SBpe=SBpe
        self.SBot=SBot
        self.SBroe=SBroe
        self.SBotka=SBotka
        
        
        self.Sort_CB_conditions_set = True
    
    def __repr__(self):
        if self.Threshold_conditions_set:
            TH_con_STR = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(\
                        self.CTGearing, self.CTOVA, self.CTPB, self.CTPE, self.CTOT, self.CTROE, self.CTOTKA)
        else:
            TH_con_STR = "NOT SET\n"
        
        
        if self.Sort_CB_conditions_set:
            Sort_CB_con = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(\
                        self.SBgearing, self.SBova, self.SBpb, self.SBpe, self.SBot, self.SBroe, self.SBotka)
        else:
            Sort_CB_con = "NOT SET\n"
        
        
        if self.Show_CB_conditions_set:
            CB_con_STR1 = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(\
                self.ShowGearingFail, self.ShowOVAFail, self.ShowROEFail, self.ShowViisiOsinkoaFail, \
                self.ShowTulosNousuFail, self.ShowPassedTrim, self.ShowHandpicked)
            
            CB_con_STR2 = "{}\t{}\t{}\t{}\t{}\t{}\n".format(\
                self.ShowTaKuPa, self.ShowTaKuTa, self.ShowTaPeTe, self.ShowTaRaho, self.ShowTaTekn, self.ShowTaTePa)
            
            CB_con_STR3 = "{}\t{}\t{}\t{}\t{}\n".format(\
                self.ShowTaTeHu, self.ShowTaTiLiPa, self.ShowTaYlPa, self.ShowTaOlKa, self.ShowTaUnknown)
            
            CB_con_STR4 = "{}\t{}".format(\
                self.ShowFailedSort, self.ShowPassedSort)
        else:
            CB_con_STR1 = "NOT SET\n"
            CB_con_STR2 = "NOT SET\n"
            CB_con_STR3 = "NOT SET\n"
            CB_con_STR4 = "NOT SET"
        
        
        repr_str = "\tThreshold_conditions:\n" +\
            TH_con_STR +\
            "\tSort_CB_conditions:\n" +\
            Sort_CB_con +\
            "\tShow_CB_conditions:\n" +\
            CB_con_STR1 +\
            CB_con_STR2 +\
            CB_con_STR3 +\
            CB_con_STR4
        
        return repr_str
