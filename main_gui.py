import os, sys, logging
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import scrape_KL


class Window(QWidget):
    def __init__(self, src_dir):
        super().__init__()
        self.scrapes_dir = src_dir + '\scrapes'
        self.setWindowTitle('Osakkeiden loytaminen Kauppalehdesta')
        self.setMinimumSize(700,350)
        self.setMaximumSize(950,450)
        self.setWindow()

    def setWindow(self):
        ScrapeButton        =QPushButton("Scrape companies")
        LoadButton          =QPushButton("Load companies from csv-file")
        SaveButton          =QPushButton("Save companies to csv-file") # TODO: Remove
        KarsiButton         =QPushButton("Filter companies")
        JarjestaButton      =QPushButton("Organize companies")
        PrintCompaniesButton =QPushButton("Print companies")
        PrintInfo           =QPushButton("Print company info")
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
        self.company_ID=QLineEdit(self)
        hbox1=QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(lblID)
        hbox1.addWidget(self.company_ID)
        hbox1.addWidget(PrintInfo)
        hbox1.addStretch(1)
        
        self.FileComboBox=QComboBox()
        self.nullFile = 'CSV-files in "scrapes" folder'
        self.FileComboBox.addItem(self.nullFile)
        SaveFiles = os.listdir("scrapes")
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
        self.FileComboBox.addItem(self.nullFile)
        SaveFiles = os.listdir("scrapes")
        self.FileComboBox.addItems(SaveFiles)

    def ButtonClicked(self):
        sender=self.sender()
        if self.FileComboBox.currentText() == self.nullFile:
            self.csv_filename = None
        else:
            self.csv_filename = "scrapes\\" + self.FileComboBox.currentText()

        if sender.text() == "Scrape companies":
            c = 1/0
            new_csv_filename = scrape_KL.scrape_companies(self.scrapes_dir)
            if new_csv_filename:
                # TODO: change selected csv_filename to the returned filename
                logger.debug("new_csv_filename: " + new_csv_filename)
            else:
                logger.debug("Scraping failed.")
        elif sender.text() == "Exit":
            self.close()
        else:
            if not self.csv_filename:
                logger.info("No csv-file.")
            else:
                if sender.text() == "Load companies from csv-file":
                    scrape_KL.load_companies(self.csv_filename)
                elif sender.text() == "Save companies to csv-file":
                    logger.debug("FEATURE WILL BE REMOVED: Companies will be automatically stored.")
                elif sender.text() == "Filter companies":
                    scrape_KL.filter_companies(self.csv_filename)
                elif sender.text() == "Organize companies":
                    scrape_KL.organize_companies(self.csv_filename)
                elif sender.text() == "Print companies":
                    scrape_KL.print_companies(self.csv_filename)
                elif sender.text() == "Print company info":
                    try:
                        company_ID = int(self.company_ID.text())
                        scrape_KL.print_company(self.csv_filename, company_ID)
                    except ValueError:
                        logger.info("The company-ID must be an integer.")
                else:
                    logger.debug('Did not recognize "sender.text()": ' + sender.text())


if __name__ == '__main__':
    logger = logging.getLogger('root')
    logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
    logger.setLevel(logging.DEBUG)
    #logger.setLevel(logging.INFO)

    #Creates a "scrapes"-folder if one does not exist.
    if not os.path.isdir("scrapes"):
        os.makedirs("scrapes")
        logger.debug('"scrapes" folder created')

    app = QApplication(sys.argv)
    Window = Window(os.path.dirname(os.path.abspath(__file__)))
    Window.show()
    sys.exit(app.exec_())
