class Costum_conditions():
    def __init__(self):
        self.Threshold_conditions_set = False
        self.Checkbox_conditions_set  = False
    
    def set_Threshold_conditions(self, \
            CTGearing, CTOVA, CTPB, CTPE, CTOT, CTROE):
        
        self.CTGearing = CTGearing
        self.CTOVA = CTOVA
        self.CTPB = CTPB
        self.CTPE = CTPE
        self.CTOT = CTOT
        self.CTROE = CTROE
        
        self.Threshold_conditions_set = True
    
    def set_Checkbox_conditions(self, \
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
        
        
        
        self.Checkbox_conditions_set  = True
    
    def __repr__(self):
        TH_con_STR = "{}\t{}\t{}\t{}\t{}\t{}\n".format(\
                    self.CTGearing, self.CTOVA, self.CTPB, self.CTPE, self.CTOT, self.CTROE)
        
        CB_con_STR1 = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(\
            self.ShowGearingFail, self.ShowOVAFail, self.ShowROEFail, self.ShowViisiOsinkoaFail, \
            self.ShowTulosNousuFail, self.ShowPassedTrim, self.ShowHandpicked)
        
        CB_con_STR2 = "{}\t{}\t{}\t{}\t{}\t{}\n".format(\
            self.ShowTaKuPa, self.ShowTaKuTa, self.ShowTaPeTe, self.ShowTaRaho, self.ShowTaTekn, self.ShowTaTePa)
        
        CB_con_STR3 = "{}\t{}\t{}\t{}\t{}\n".format(\
            self.ShowTaTeHu, self.ShowTaTiLiPa, self.ShowTaYlPa, self.ShowTaOlKa, self.ShowTaUnknown)
        
        CB_con_STR4 = "{}\t{}".format(\
            self.ShowFailedSort, self.ShowPassedSort)
        
        
        repr_str = "\tThreshold_conditions:\n" +\
            TH_con_STR +\
            "\tCheckbox_conditions:\n" +\
            CB_con_STR1 +\
            CB_con_STR2 +\
            CB_con_STR3 +\
            CB_con_STR4
        
        return repr_str
