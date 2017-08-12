import os, sys, logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.Qt import pyqtSignal, QThread
from datetime import date

import scrapeKL
import scraping

import time, traceback

class ScrapeGuiException(Exception):
    pass


class scrapeThread(QThread):

    def __init__(self, storage_directory, company_names):
        QThread.__init__(self)
        self.storage_directory = storage_directory
        self.company_names = company_names

    def __del__(self): # TODO: Is this needed?
        self.wait()

    def run(self):
        logger.debug("Starting scrapeing from QThread")
        _json_metrics_list, _failed_company_dict, _metricsfilename = scrapeKL.scrape_companies(self.storage_directory, self.company_names)


class Window(QWidget):
    terminate_scraping_sig = pyqtSignal()

    def __init__(self, storage_directory):
        super().__init__()
        self.storage_directory = storage_directory
        self.tsv_filename = None
        self.setWindowTitle('OsakkeetScraper Kauppalehdesta')
        self.setWindow()
        self.setLoggingLevel()
        self.refreshFileComboBox()
        self.setNewestTsvFileFromToday()
        self.setScraping()

    def setScraping(self):
        self.scraping_terminated = False
        company_names = {}
        #company_names = {2048:"talenom", 1906:"cargotec", 1196:"afarak group"}
        self.scrapeThread = scrapeThread(self.storage_directory, company_names)
        self.scrapeThread.finished.connect(self.scrapingDone)

    def scrapingDone(self):
        if self.scraping_terminated:
            time.sleep(1)
        else:
            self.refreshFileComboBox()
            self.FileComboBox.setCurrentIndex(1)
        self.ScrapeButton.setText(self.scrape_str)

    def setWindow(self):
        # strings
        self.scrape_str                 = "Scrape companies"
        self.stop_scraping_str          = "Stop scraping"
        self.printCompanies_str         = "Print companies"
        self.printMetrics_str           = "metrics"
        self.printMetricsSimple_str     = "metrics simple"
        self.printCalculations_str      = "calculations"
        self.filter_str                 = "Filter companies"
        self.organize_str               = "Organize companies"
        self.exit_str                   = "Exit"
        self.null_filename              = "Select TSV-file"

        # buttons
        self.ScrapeButton           = QPushButton(self.scrape_str)
        PrintCompaniesButton        = QPushButton(self.printCompanies_str)
        PrintMetricsButton          = QPushButton(self.printMetrics_str)
        PrintMetricsSimpleButton    = QPushButton(self.printMetricsSimple_str)
        PrintCalculationsButton     = QPushButton(self.printCalculations_str)
        FilterButton                = QPushButton(self.filter_str)
        OrganizeButton              = QPushButton(self.organize_str)
        ExitButton                  = QPushButton(self.exit_str)

        # other widgets
        self.DebugCheckBox = QCheckBox("DEBUG")
        self.DebugCheckBox.setCheckState(Qt.Checked)
        self.ScrapingProgressBar = QProgressBar()
        self.CompanySearchLineEdit = QLineEdit(self)
        self.FileComboBox = QComboBox()
        self.FileComboBox.setMaxVisibleItems(30)

        # connect buttons and widgets
        self.ScrapeButton.clicked.connect(self.buttonClicked)
        PrintCompaniesButton.clicked.connect(self.buttonClicked)
        PrintMetricsButton.clicked.connect(self.buttonClicked)
        PrintMetricsSimpleButton.clicked.connect(self.buttonClicked)
        PrintCalculationsButton.clicked.connect(self.buttonClicked)
        FilterButton.clicked.connect(self.buttonClicked)
        OrganizeButton.clicked.connect(self.buttonClicked)
        ExitButton.clicked.connect(self.buttonClicked)
        self.DebugCheckBox.stateChanged.connect(self.setLoggingLevel)
        self.FileComboBox.currentTextChanged.connect(self.setTsvFilename)

        # layout boxes
        hbox_StoredFiles = QHBoxLayout()
        hbox_StoredFiles.addWidget(self.FileComboBox)
        hbox_PrintMetrics = QHBoxLayout()
        hbox_PrintMetrics.addWidget(QLabel("Company Print:"))
        hbox_PrintMetrics.addWidget(self.CompanySearchLineEdit)
        hbox_PrintMetrics.addWidget(PrintMetricsButton)
        hbox_PrintMetrics.addWidget(PrintMetricsSimpleButton)
        hbox_PrintMetrics.addWidget(PrintCalculationsButton)

        # layout
        space = 15
        vbox_main = QVBoxLayout()
        vbox_main.addWidget(self.DebugCheckBox)
        #vbox_main.addWidget(self.ScrapingProgressBar)
        vbox_main.addWidget(self.ScrapeButton)
        vbox_main.addLayout(hbox_StoredFiles)
        vbox_main.addSpacing(space)
        vbox_main.addWidget(PrintCompaniesButton)
        vbox_main.addLayout(hbox_PrintMetrics)
        vbox_main.addSpacing(space)
        vbox_main.addWidget(FilterButton)
        vbox_main.addWidget(OrganizeButton)
        vbox_main.addSpacing(space)
        vbox_main.addWidget(ExitButton)
        vbox_main.addStretch(1)
        hbox_main = QHBoxLayout()
        hbox_main.addLayout(vbox_main)
        hbox_main.addStretch(1)
        self.setLayout(hbox_main)

    def setLoggingLevel(self):
        if self.DebugCheckBox.isChecked():
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def refreshFileComboBox(self):
        i = self.FileComboBox.count()
        while i > 0:
            self.FileComboBox.removeItem(0)
            i -= 1
        self.FileComboBox.addItem(self.null_filename)
        all_filenames = os.listdir(self.storage_directory)
        stored_filenames = []
        for f in reversed(all_filenames):
            if f.endswith(".tsv") and f.startswith("scrape_metrics"):
                stored_filenames.append(f)
        self.FileComboBox.addItems(stored_filenames)

    def setNewestTsvFileFromToday(self):
        if len(self.FileComboBox) > 1:
            s = "scrape_metrics_" + date.today().strftime(scraping.date_format) # YYYY-MM-DD
            if self.FileComboBox.itemText(1).startswith(s):
                self.FileComboBox.setCurrentIndex(1)

    def setTsvFilename(self):
        if self.FileComboBox.currentText() == self.null_filename:
            self.tsv_filename = None
        else:
            self.tsv_filename = "{}\\{}".format(self.storage_directory, self.FileComboBox.currentText())

    def buttonClicked(self):
        sender = self.sender()
        if sender.text() == self.scrape_str:
            self.ScrapeButton.setText(self.stop_scraping_str)
            self.ScrapingProgressBar.setValue(0)
            self.companies_scraped = 0
            self.scraping_started_time = time.time()
            self.scrapeThread.start()
        elif sender.text() == self.stop_scraping_str:
            logger.info("Scraping terminated")
            self.scraping_terminated = True
            self.scrapeThread.terminate()
        elif sender.text() == self.exit_str:
            self.close()
        elif self.tsv_filename:
            print_type = None
            company_id = None
            company_name = None
            if sender.text() == self.filter_str:
                scrapeKL.filter_companies(self.tsv_filename)
            elif sender.text() == self.organize_str:
                scrapeKL.organize_companies(self.tsv_filename)
            elif sender.text() == self.printCompanies_str:
                scrapeKL.print_companies(self.tsv_filename)
            elif sender.text() == self.printMetrics_str:
                print_type = "metrics"
            elif sender.text() == self.printMetricsSimple_str:
                print_type = "metrics_simple"
            elif sender.text() == self.printCalculations_str:
                print_type = "calculations"
            else:
                raise ScrapeGuiException('Unexpected "sender.text()": [{}]'.format(sender.text()))
            if print_type != None:
                search_line_str = self.CompanySearchLineEdit.text().strip()
                if search_line_str != "":
                    try:
                        company_id = int(search_line_str)
                    except ValueError:
                        company_name = search_line_str
                scrapeKL.print_company_metrics(self.tsv_filename, print_type, company_id, company_name)
        else:
            logger.info("No TSV-file selected")


if __name__ == '__main__':
    logger = logging.getLogger('root')
    logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
    logger.setLevel(logging.DEBUG)

    storage_directory = "scrapes"
    #Creates a storage-folder if one does not exist.
    if not os.path.isdir(storage_directory):
        os.makedirs(storage_directory)
        logger.debug("storage-folder created: [{}]".format(storage_directory))

    app = QApplication(sys.argv)
    Window = Window(storage_directory)
    Window.show()
    sys.exit(app.exec_())
