from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import os

#import webbrowser

from print_and_error_functions import *
from scraping_functions import *
from manage_files import *
from yritys_luokka import *

from scrape_KL import *



class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Osakkeiden loytaminen Kauppalehdesta')
        
        self.setMinimumSize(700,350)
        self.setMaximumSize(950,450)
        
        self.Tiedot=False
        
        self.setWindow()
    
    def setWindow(self):
        ScrapeButton        =QPushButton("Scrape companies")
        LoadButton          =QPushButton("Load companies from csv-file")
        SaveButton          =QPushButton("Save companies to csv-file")
        PrintCompaniesButton =QPushButton("Print companies")
        PrintInfo           =QPushButton("Print the companys info")
        KarsiButton         =QPushButton("Karsi")
        JarjestaButton      =QPushButton("Jarjesta")
        ExitButton          =QPushButton("Exit")
        
        ScrapeButton.clicked.connect(self.ButtonClicked)
        LoadButton.clicked.connect(self.ButtonClicked)
        SaveButton.clicked.connect(self.ButtonClicked)
        PrintCompaniesButton.clicked.connect(self.ButtonClicked)
        PrintInfo.clicked.connect(self.ButtonClicked)
        KarsiButton.clicked.connect(self.ButtonClicked)
        JarjestaButton.clicked.connect(self.ButtonClicked)
        ExitButton.clicked.connect(self.ButtonClicked)
        
        lblID=QLabel("ID")
        self.ID=QLineEdit(self)
        hbox1=QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(lblID)
        hbox1.addWidget(self.ID)
        hbox1.addWidget(PrintInfo)
        hbox1.addStretch(1)
        
        self.FileComboBox=QComboBox()
        self.FileComboBox.addItem('CSV-files in "stored_scrapes" folder')
        SaveFiles = os.listdir("stored_scrapes")
        self.FileComboBox.addItems(SaveFiles)
        
        self.RefreshButton=QPushButton("Refresh")
        self.RefreshButton.clicked.connect(self.RefreshFileComboBox)
        
        hboxRF=QHBoxLayout()
        hboxRF.addWidget(self.FileComboBox)
        hboxRF.addWidget(self.RefreshButton)
        
        sidesTop=   "--------------------------------------"
        
        #Left side
        vbox=QVBoxLayout()
        vbox.addWidget(QLabel(sidesTop))
        vbox.addSpacing(40)
        vbox.addWidget(ScrapeButton)
        vbox.addSpacing(20)
        vbox.addWidget(SaveButton)
        vbox.addSpacing(20)
        vbox.addWidget(PrintCompaniesButton)
        vbox.addStretch(1)
        
        
        #Middle
        vbox2=QVBoxLayout()
        vbox2.addSpacing(60)
        vbox2.addLayout(hboxRF)
        vbox2.addWidget(LoadButton)
        vbox2.addSpacing(40)
        vbox2.addLayout(hbox1)
        vbox2.addStretch(1)
        vbox2.addWidget(ExitButton)
        vbox2.addSpacing(60)
        
        
        #Right side
        vbox3=QVBoxLayout()
        vbox3.addWidget(QLabel(sidesTop))
        vbox3.addSpacing(40)
        vbox3.addWidget(KarsiButton)
        vbox3.addSpacing(40)
        vbox3.addWidget(JarjestaButton)
        vbox3.addStretch(1)
        
        
        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addSpacing(50)
        hbox.addLayout(vbox2)
        hbox.addSpacing(50)
        hbox.addLayout(vbox3)
        hbox.addStretch(1)
        
        self.setLayout(hbox)
    
    def RefreshFileComboBox(self):
        i=self.FileComboBox.count()
        while i>0:
            self.FileComboBox.removeItem(0)
            i-=1
        
        self.FileComboBox.addItem('CSV-files in "stored_scrapes" folder')
        SaveFiles = os.listdir("stored_scrapes")
        self.FileComboBox.addItems(SaveFiles)
    
    def ButtonClicked(self):
        sender=self.sender()
        print("\n\n\n\n\n\n\n\n\n")
        
        if sender.text() == "Scrape companies":
            DICT_yritys = scrape_yritys_dict()
            DICT_YRITYKSEN_TIEDOT, scraped_IDs = scrape_DICT_YRITYKSEN_TIEDOT_AND_scraped_IDs(DICT_yritys)
            
            self.Tiedot=Tiedot_luokka()
            self.Tiedot.set_from_scrape(DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys)
            print("TIEDOT scraped from Kauppalehti.")
        elif sender.text() == "Load companies from csv-file":
            if self.FileComboBox.currentText() == 'Files in "stored_scrapes" folder':
                print("Nothing is choosen.")
            else:
                filename = "stored_scrapes\\" + self.FileComboBox.currentText()
                
                self.Tiedot=Tiedot_luokka()
                self.Tiedot.set_from_csv_file(filename)
                
                print("TIEDOT has been loaded from the file: {}".format(filename))
        elif sender.text() == "Save companies to csv-file":
            if self.Tiedot:
                self.Tiedot.save_to_csv_file()
            else:
                print("TIEDOT is missing")
        elif sender.text() == "Print companies":
            if self.Tiedot:
                for ID in self.Tiedot.scraped_IDs:
                    print("{} {}".format(ID, self.Tiedot.DICT_yritys[ID]))
            else:
                print("TIEDOT is missing")
        elif sender.text() == "Print the companys info":
            if self.Tiedot:
                try:
                    ID=int(self.ID.text())
                    if ID in self.Tiedot.scraped_IDs:
                        print("{} {}".format(ID, self.Tiedot.DICT_yritys[ID]))
                        matrix_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID][0])
                        kurssi_tiedot_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
                        kurssi_tulostiedot_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
                    else:
                        print("There is no company scraped with ID: {}".format(ID))
                except ValueError:
                    print("The ID must be an int.")
            else:
                print("TIEDOT is missing")
        elif sender.text() == "Karsi":
            print("Karsi")
        elif sender.text() == "Jarjesta":
            print("Jarjesta")
        elif sender.text() == "Exit":
            self.close()


if __name__ == '__main__':
    #Creates a "stored_scrapes"-folder if one does not exist.
    if not os.path.isdir("stored_scrapes"):
        os.makedirs("stored_scrapes")
        print('"stored_scrapes" folder created')
    
    app = QApplication(sys.argv)
    Window = Window()
    Window.show()
    sys.exit(app.exec_())