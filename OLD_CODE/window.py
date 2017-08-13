import os, sys
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, \
    QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox, QGridLayout, \
    QApplication



class Window(QWidget):
    def __init__(self, kaytetaan=None):
        super().__init__()
        self.setWindowTitle('Osakkeiden loytaminen Kauppalehdesta')
        
        self.setMinimumSize(700,350)
        #self.setMaximumSize(950,450)
        
        self.kaytetaan = kaytetaan
        
        self.setWindow()
    
    def setWindow(self):
        layoutMAIN = self.setMainLayout()
        
        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(layoutMAIN)
        hbox.addStretch(1)
        
        """
        layoutSIDE =self.setSideLayout()
        
        hbox.addLayout(layoutSIDE)
        hbox.addStretch(1)
        """
        
        self.setLayout(hbox)
    
    def setMainLayout(self):
        vboxDATA = self.set_vBoxDATA()
        vboxPCI = self.set_vboxPCI()
        vboxCP = self.set_vboxCP()
        
        
        vboxMAIN=QVBoxLayout()
        vboxMAIN.addLayout(vboxDATA)
        vboxMAIN.addStretch(1)
        vboxMAIN.addLayout(vboxPCI)
        vboxMAIN.addStretch(1)
        vboxMAIN.addLayout(vboxCP)
        
        return vboxMAIN
    
    def setSideLayout(self):
        sideTop = "-" *40
        
        DoTestButton            =QPushButton("DO TEST")
        DoTestButton.clicked.connect(self.WindowFunction)
        
        
        vboxSIDE=QVBoxLayout()
        vboxSIDE.addWidget(QLabel(sideTop))
        vboxSIDE.addSpacing(20)
        vboxSIDE.addWidget(DoTestButton)
        vboxSIDE.addStretch(1)
        
        return vboxSIDE
    
    def set_vBoxDATA(self):
        ScrapeButton    =QPushButton("Scrape companies (saves to csv-file when scraped)")
        LoadButton      =QPushButton("Load companies from csv-file")
        
        ScrapeButton.clicked.connect(self.WindowFunction)
        LoadButton.clicked.connect(self.WindowFunction)
        
        
        self.FileComboBox=QComboBox()
        self.FileComboBox.addItem('CSV-files in "Saved_data" folder')
        #SaveFiles = os.listdir("Saved_data")
        SaveFiles = ["dir1", "dir2"]
        self.FileComboBox.addItems(SaveFiles)
        
        self.RefreshButton=QPushButton("Refresh")
        self.RefreshButton.clicked.connect(self.RefreshFileComboBox)
        
        hboxRF=QHBoxLayout()
        hboxRF.addWidget(self.FileComboBox)
        hboxRF.addWidget(self.RefreshButton)
        
        
        vboxDATA=QVBoxLayout()
        vboxDATA.addWidget(ScrapeButton)
        vboxDATA.addSpacing(20)
        vboxDATA.addLayout(hboxRF)
        vboxDATA.addWidget(LoadButton)
        
        return vboxDATA
    
    def set_vboxPCI(self):
        #PCI = Print Company Info
        self.ID=QLineEdit(self)
        
        PrintRawButton      =QPushButton("RAW")
        PrintFormatedButton =QPushButton("FORMATED")
        PrintTrimmedButton  =QPushButton("TRIMMED")
        PrintSortedButton   =QPushButton("SORTED")
        PrintAllButton      =QPushButton("ALL")
        
        PrintRawButton.clicked.connect(self.PrintInfoButtonClicked)
        PrintFormatedButton.clicked.connect(self.PrintInfoButtonClicked)
        PrintTrimmedButton.clicked.connect(self.PrintInfoButtonClicked)
        PrintSortedButton.clicked.connect(self.PrintInfoButtonClicked)
        PrintAllButton.clicked.connect(self.PrintInfoButtonClicked)
        
        
        hboxPCI=QHBoxLayout()
        hboxPCI.addStretch(1)
        hboxPCI.addWidget(QLabel("ID"))
        hboxPCI.addWidget(self.ID)
        hboxPCI.addWidget(PrintRawButton)
        hboxPCI.addWidget(PrintFormatedButton)
        hboxPCI.addWidget(PrintTrimmedButton)
        hboxPCI.addWidget(PrintSortedButton)
        hboxPCI.addWidget(PrintAllButton)
        hboxPCI.addStretch(1)
        
        vboxPCI=QVBoxLayout()
        vboxPCI.addWidget(QLabel("\t\tPrint Companys Info"))
        vboxPCI.addLayout(hboxPCI)
        
        return vboxPCI
    
    def set_vboxCP(self):
        #CP = Costum Print
        PrintCompaniesInfoButton    =QPushButton("Print COMPANIES INFO")
        PrintCompaniesInfoButton.clicked.connect(self.WindowFunction)
        
        
        vboxTrimCBs = self.set_vboxTrimCBs()
        vboxToimialaCBs = self.set_vboxToimialaCBs()
        vboxOtherCBs = self.set_vboxOtherCBs()
        vboxCT = self.set_vboxCTandSortCBs()
        
        hboxCB=QHBoxLayout()
        hboxCB.addLayout(vboxTrimCBs)
        hboxCB.addLayout(vboxToimialaCBs)
        hboxCB.addLayout(vboxOtherCBs)
        hboxCB.addLayout(vboxCT)
        
        
        vboxCP=QVBoxLayout()
        vboxCP.addWidget(PrintCompaniesInfoButton)
        vboxCP.addSpacing(10)
        vboxCP.addLayout(hboxCB)
        
        return vboxCP
    
    def set_vboxTrimCBs(self):
        #Trim Checkboxes
        self.TrimFailCBs=[]
        
        self.CheckAllTrimFailsButton=QPushButton("Check/Uncheck ALL")
        self.CheckAllTrimFailsButton.clicked.connect(lambda: self.CheckAllCBs(self.TrimFailCBs))
        
        self.ShowGFailCB=QCheckBox("Gearing")
        self.ShowOFailCB=QCheckBox("Omavaraisuusaste")
        self.ShowRFailCB=QCheckBox("ROE")
        self.ShowJFailCB=QCheckBox("Jaettu viisi vuotta osinkoa")
        self.ShowTFailCB=QCheckBox("Tulokset nousee viisi vuotta")
        self.ShowTRIMPassCB=QCheckBox("Passed TRIM")
        self.ShowHANDPICKCB=QCheckBox("HANDPICK")
        
        self.TrimFailCBs.append(self.ShowGFailCB)
        self.TrimFailCBs.append(self.ShowOFailCB)
        self.TrimFailCBs.append(self.ShowRFailCB)
        self.TrimFailCBs.append(self.ShowJFailCB)
        self.TrimFailCBs.append(self.ShowTFailCB)
        self.TrimFailCBs.append(self.ShowTRIMPassCB)
        self.TrimFailCBs.append(self.ShowHANDPICKCB)
        
        
        for CB in self.TrimFailCBs:
            CB.setCheckState(Qt.Unchecked)
        self.ShowTRIMPassCB.setCheckState(Qt.Checked)
        self.ShowHANDPICKCB.setCheckState(Qt.Checked)
        
        
        vboxTrimCBs=QVBoxLayout()
        vboxTrimCBs.addWidget(QLabel("Show TRIM Fails:"))
        vboxTrimCBs.addWidget(self.CheckAllTrimFailsButton)
        for CB in self.TrimFailCBs:
            vboxTrimCBs.addWidget(CB)
        vboxTrimCBs.addStretch(1)
        
        return vboxTrimCBs
    
    def set_vboxToimialaCBs(self):
        #Toimiala Checkboxes
        self.ToimialaCBs=[]
        
        self.listaToimialoista=["Kulutuspalvelut","Kulutustavarat","Perusteollisuus","Rahoitus",\
        "Teknologia","Teollisuustuotteet ja -palvelut","Terveydenhuolto",\
        "Tietoliikennepalvelut","Yleishyodylliset palvelut","Oljy ja kaasu", "UNKNOWN"]
        
        self.CheckAllToimialatButton=QPushButton("Check/Uncheck ALL")
        self.CheckAllToimialatButton.clicked.connect(lambda: self.CheckAllCBs(self.ToimialaCBs))
        
        self.ShowToimialaKulutuspalvelutCB=QCheckBox(self.listaToimialoista[0])
        self.ShowToimialaKulutustavaratCB=QCheckBox(self.listaToimialoista[1])
        self.ShowToimialaPerusteollisuusCB=QCheckBox(self.listaToimialoista[2])
        self.ShowToimialaRahoitusCB=QCheckBox(self.listaToimialoista[3])
        self.ShowToimialaTeknologiaCB=QCheckBox(self.listaToimialoista[4])
        self.ShowToimialaTeollisuustuotteet_palvelutCB=QCheckBox(self.listaToimialoista[5])
        self.ShowToimialaTerveydenhuoltoCB=QCheckBox(self.listaToimialoista[6])
        self.ShowToimialaTietoliikennepalvelutCB=QCheckBox(self.listaToimialoista[7])
        self.ShowToimialaYleishyodyllisetCB=QCheckBox(self.listaToimialoista[8])
        self.ShowToimialaOljy_kaasuCB=QCheckBox(self.listaToimialoista[9])
        self.ShowToimialaUnknown=QCheckBox(self.listaToimialoista[10])
        
        self.ToimialaCBs.append(self.ShowToimialaKulutuspalvelutCB)
        self.ToimialaCBs.append(self.ShowToimialaKulutustavaratCB)
        self.ToimialaCBs.append(self.ShowToimialaPerusteollisuusCB)
        self.ToimialaCBs.append(self.ShowToimialaRahoitusCB)
        self.ToimialaCBs.append(self.ShowToimialaTeknologiaCB)
        self.ToimialaCBs.append(self.ShowToimialaTeollisuustuotteet_palvelutCB)
        self.ToimialaCBs.append(self.ShowToimialaTerveydenhuoltoCB)
        self.ToimialaCBs.append(self.ShowToimialaTietoliikennepalvelutCB)
        self.ToimialaCBs.append(self.ShowToimialaYleishyodyllisetCB)
        self.ToimialaCBs.append(self.ShowToimialaOljy_kaasuCB)
        self.ToimialaCBs.append(self.ShowToimialaUnknown)
        
        
        for CB in self.ToimialaCBs:
            CB.setCheckState(Qt.Checked)
        self.ShowToimialaRahoitusCB.setCheckState(Qt.Unchecked)
        
        
        vboxToimialaCBs=QVBoxLayout()
        vboxToimialaCBs.addWidget(QLabel("Show Toimialat:"))
        vboxToimialaCBs.addWidget(self.CheckAllToimialatButton)
        for CB in self.ToimialaCBs:
            vboxToimialaCBs.addWidget(CB)
        vboxToimialaCBs.addStretch(1)
        
        return vboxToimialaCBs
    
    def set_vboxOtherCBs(self):
        #Other Checkboxes
        self.ShowFailedSortCB=QCheckBox("Failed Sort")
        self.ShowPassedSortCB=QCheckBox("Passed Sort")
        
        self.OtherCBs=[]
        self.OtherCBs.append(self.ShowFailedSortCB)
        self.OtherCBs.append(self.ShowPassedSortCB)
        
        
        for CB in self.OtherCBs:
            CB.setCheckState(Qt.Checked)
        self.ShowFailedSortCB.setCheckState(Qt.Unchecked)
        
        
        vboxOtherCBs=QVBoxLayout()
        vboxOtherCBs.addWidget(QLabel("Show Others:"))
        vboxOtherCBs.addWidget(self.ShowFailedSortCB)
        for CB in self.OtherCBs:
            vboxOtherCBs.addWidget(CB)
        vboxOtherCBs.addStretch(2)
        
        return vboxOtherCBs
    
    def set_vboxCTandSortCBs(self):
        #Costum thresholds Fields
        self.CTGearing=QLineEdit()
        self.CTOVA=QLineEdit()
        self.CTPB=QLineEdit()
        self.CTPE=QLineEdit()
        self.CTOT=QLineEdit()
        self.CTROE=QLineEdit()
        self.CTOTKA=QLineEdit()
        
        #Sort by Checkboxes
        self.SBgearingCB=QCheckBox()
        self.SBovaCB=QCheckBox()
        self.SBpbCB=QCheckBox()
        self.SBpeCB=QCheckBox()
        self.SBotCB=QCheckBox()
        self.SBroeCB=QCheckBox()
        self.SBotkaCB=QCheckBox()
        
        self.SBpbCB.setCheckState(Qt.Checked)
        self.SBpeCB.setCheckState(Qt.Checked)
        self.SBotCB.setCheckState(Qt.Checked)
        self.SBroeCB.setCheckState(Qt.Checked)
        
        
        grid=QGridLayout()
        grid.addWidget(QLabel("Costum Thresholds:"), 0, 1)
        grid.addWidget(QLabel("Sorted by:"), 0, 2)
        
        grid.addWidget(QLabel("Gearing\t(MAX)"), 1, 0)
        grid.addWidget(self.CTGearing, 1, 1)
        grid.addWidget(self.SBgearingCB, 1, 2)
        
        grid.addWidget(QLabel("OVA\t(MIN)"), 2, 0)
        grid.addWidget(self.CTOVA, 2, 1)
        grid.addWidget(self.SBovaCB, 2, 2)
        
        grid.addWidget(QLabel("P/B\t(MAX)"), 3, 0)
        grid.addWidget(self.CTPB, 3, 1)
        grid.addWidget(self.SBpbCB, 3, 2)
        
        grid.addWidget(QLabel("P/E\t(MAX)"), 4, 0)
        grid.addWidget(self.CTPE, 4, 1)
        grid.addWidget(self.SBpeCB, 4, 2)
        
        grid.addWidget(QLabel("Osinkot.\t(MIN)"), 5, 0)
        grid.addWidget(self.CTOT, 5, 1)
        grid.addWidget(self.SBotCB, 5, 2)
        
        grid.addWidget(QLabel("ROE\t(MIN)"), 6, 0)
        grid.addWidget(self.CTROE, 6, 1)
        grid.addWidget(self.SBroeCB, 6, 2)
        
        grid.addWidget(QLabel("Osinkot. ka5 (MIN)"), 7, 0)
        grid.addWidget(self.CTOTKA, 7, 1)
        grid.addWidget(self.SBotkaCB, 7, 2)
        
        
        vbox=QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch(1)
        
        return vbox
    
    
    def CheckAllCBs(self, CBsList):
        if CBsList[0].checkState() == Qt.Checked:
            for CB in CBsList:
                CB.setCheckState(Qt.Unchecked)
        else:
            for CB in CBsList:
                CB.setCheckState(Qt.Checked)
    
    def RefreshFileComboBox(self):
        i=self.FileComboBox.count()
        while i>0:
            self.FileComboBox.removeItem(0)
            i-=1
        
        self.FileComboBox.addItem('CSV-files in "Saved_data" folder')
        SaveFiles = os.listdir("Saved_data")
        self.FileComboBox.addItems(SaveFiles)
    
    def set_conditions(self):
        self.get_Costum_Thresholds_conditions()
        self.get_Show_CB_conditions()
        self.get_Sort_CB_conditions()
    
    def get_Costum_Thresholds_conditions(self):
        try:
            CTGearing=float(self.CTGearing.text())
        except ValueError:
            CTGearing=1000
        
        try:
            CTOVA=float(self.CTOVA.text())
        except ValueError:
            CTOVA=-1000
        
        try:
            CTPB=float(self.CTPB.text())
        except ValueError:
            CTPB=1000
        
        try:
            CTPE=float(self.CTPE.text())
        except ValueError:
            CTPE=1000
        
        try:
            CTOT=float(self.CTOT.text())
        except ValueError:
            CTOT=-1000
        
        try:
            CTROE=float(self.CTROE.text())
        except ValueError:
            CTROE=-1000
        
        try:
            CTOTKA=float(self.CTOTKA.text())
        except ValueError:
            CTOTKA=-1000
        
        
        self.kaytetaan.Conditions.set_Threshold_conditions(\
                        CTGearing, CTOVA, CTPB, CTPE, CTOT, CTROE, CTOTKA)
    
    def get_Show_CB_conditions(self):
        ShowGearingFail =       self.ShowGFailCB.checkState() == Qt.Checked
        ShowOVAFail =           self.ShowOFailCB.checkState() == Qt.Checked
        ShowROEFail =           self.ShowRFailCB.checkState() == Qt.Checked
        ShowViisiOsinkoaFail =  self.ShowJFailCB.checkState() == Qt.Checked
        ShowTulosNousuFail =    self.ShowTFailCB.checkState() == Qt.Checked
        ShowPassedTrimFail =    self.ShowTRIMPassCB.checkState() == Qt.Checked
        ShowHandpicked =        self.ShowHANDPICKCB.checkState() == Qt.Checked
        
        ShowTaKuPa =    self.ShowToimialaKulutuspalvelutCB.checkState() == Qt.Checked
        ShowTaKuTa =    self.ShowToimialaKulutustavaratCB.checkState() == Qt.Checked
        ShowTaPeTe =    self.ShowToimialaPerusteollisuusCB.checkState() == Qt.Checked
        ShowTaRaho =    self.ShowToimialaRahoitusCB.checkState() == Qt.Checked
        ShowTaTekn =    self.ShowToimialaTeknologiaCB.checkState() == Qt.Checked
        ShowTaTePa =    self.ShowToimialaTeollisuustuotteet_palvelutCB.checkState() == Qt.Checked
        ShowTaTeHu =    self.ShowToimialaTerveydenhuoltoCB.checkState() == Qt.Checked
        ShowTaTiLiPa =  self.ShowToimialaTietoliikennepalvelutCB.checkState() == Qt.Checked
        ShowTaYlPa =    self.ShowToimialaYleishyodyllisetCB.checkState() == Qt.Checked
        ShowTaOlKa =    self.ShowToimialaOljy_kaasuCB.checkState() == Qt.Checked
        ShowTaUnknown = self.ShowToimialaUnknown.checkState() == Qt.Checked
        
        ShowFailedSort = self.ShowFailedSortCB.checkState() == Qt.Checked
        ShowPassedSort = self.ShowPassedSortCB.checkState() == Qt.Checked
        
        
        self.kaytetaan.Conditions.set_Show_CB_conditions(\
            ShowGearingFail, ShowOVAFail, ShowROEFail, ShowViisiOsinkoaFail, \
            ShowTulosNousuFail, ShowPassedTrimFail, ShowHandpicked, \
            ShowTaKuPa, ShowTaKuTa, ShowTaPeTe, ShowTaRaho, ShowTaTekn, ShowTaTePa, \
            ShowTaTeHu, ShowTaTiLiPa, ShowTaYlPa, ShowTaOlKa, ShowTaUnknown, \
            ShowFailedSort, ShowPassedSort)
    
    def get_Sort_CB_conditions(self):
        # SB = Sort by
        SBgearing = self.SBgearingCB.checkState() == Qt.Checked
        SBova =     self.SBovaCB.checkState() == Qt.Checked
        SBpb =      self.SBpbCB.checkState() == Qt.Checked
        SBpe =      self.SBpeCB.checkState() == Qt.Checked
        SBot =      self.SBotCB.checkState() == Qt.Checked
        SBroe =     self.SBroeCB.checkState() == Qt.Checked
        SBotka =    self.SBotkaCB.checkState() == Qt.Checked
        
        
        self.kaytetaan.Conditions.set_Sort_CB_conditions(\
            SBgearing, SBova, SBpb, SBpe, SBot, SBroe, SBotka)
    
    def set_cond_AND_print_comp(self):
            self.set_conditions()
            self.kaytetaan.companies_print()
    
    
    def PrintInfoButtonClicked(self):
        sender = self.sender().text()
        
        try:
            ID=int(self.ID.text())
        except ValueError:
            print("The ID must be an int.")
            return
        
        if not ID in self.kaytetaan.YRITYS_OLIO_DICT:
            print("There is no company with ID: {}".format(ID))
            return
        
        YOlio = self.kaytetaan.YRITYS_OLIO_DICT[ID]
        
        if sender == "RAW":
            YOlio.RAW_print()
        elif sender == "FORMATED":
            YOlio.FORMATED_print()
        elif sender == "TRIMMED":
            YOlio.TRIMMED_print()
        elif sender == "SORTED":
            YOlio.SORTED_print()
        elif sender == "ALL":
            YOlio.ALL_print()
    
    def WindowFunction(self):
        sender = self.sender().text()
        
        if sender == "Scrape companies (saves to csv-file when scraped)":
            self.kaytetaan.scrape_and_save()
            self.set_cond_AND_print_comp()
        
        elif sender == "Load companies from csv-file":
            if self.FileComboBox.currentText() == 'CSV-files in "Saved_data" folder':
                print("Nothing is choosen.")
                return
            
            filename = "Saved_data\\" + self.FileComboBox.currentText()
            self.kaytetaan.load(filename)
            self.set_cond_AND_print_comp()
        
        elif sender == "Print COMPANIES INFO":
            self.set_cond_AND_print_comp()
        
        
        elif sender == "DO TEST":
            #THIS IS HERE FOR POSSIBLE TESTING PURPOSES.
            print("HIDE THIS")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Window = Window()
    Window.show()
    sys.exit(app.exec_())
