import os, sys, logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.Qt import QThread, pyqtSignal
from datetime import date
import time, traceback

import scrapeKL
import scraping


class ScrapeGuiException(Exception):
    pass


class scrapeThread(QThread):

    def __init__(self, storage_directory, company_names, showProgress, terminate_scraping_sig):
        QThread.__init__(self)
        self.storage_directory = storage_directory
        self.company_names = company_names
        self.showProgress = showProgress
        self.terminate_scraping_sig = terminate_scraping_sig

    def __del__(self): # TODO: Is this needed?
        self.wait()

    def run(self):
        logger.debug("Starting scraping from QThread")
        if not self.showProgress:
            logger.info("Hide progress")
        time0 = time.time()
        _json_metrics_list, _failed_company_dict, _metricsfilename = scrapeKL.scrape_companies(
            self.storage_directory, self.company_names,
            self.showProgress, self.terminate_scraping_sig
        )
        logger.info("Scraping took: {:.2f} s".format(time.time() - time0))


class Window(QWidget):
    terminate_scraping_sig = pyqtSignal()

    def __init__(self, storage_directory):
        super().__init__()
        self.storage_directory = storage_directory
        self.filename = None
        self.setWindowTitle('OsakkeetScraper Kauppalehdesta')
        self.setWindow()
        self.setLoggingLevel()
        self.setShowProgress()
        self.refreshFileComboBox()
        self.setNewestFileFromToday()
        self.setScraping()

    def setScraping(self):
        self.scraping = False
        self.scraping_terminated = False
        company_names = {}
        #company_names = {2048:"talenom", 1906:"cargotec", 1196:"afarak group"}
        self.scrapeThread = scrapeThread(
            self.storage_directory, company_names, self.showProgress,
            self.terminate_scraping_sig
        )
        self.scrapeThread.finished.connect(self.scrapingDone)

    def startScraping(self):
        self.scraping = True
        self.ScrapeButton.setText(self.during_scraping_str)
        self.DebugCheckBox.setEnabled(False)
        self.ProgressCheckBox.setEnabled(False)
        self.FileComboBox.setEnabled(False)

        self.scrapeThread.start()

    def scrapingDone(self):
        if self.scraping_terminated:
            time.sleep(1)
            self.scraping_terminated = False
        else:
            self.refreshFileComboBox()
            self.FileComboBox.setCurrentIndex(1)

        self.ScrapeButton.setText(self.scrape_str)
        self.DebugCheckBox.setEnabled(True)
        self.ProgressCheckBox.setEnabled(True)
        self.FileComboBox.setEnabled(True)
        self.scraping = False

    def setWindow(self):
        # strings
        self.scrape_str                 = "Scrape companies"
        self.during_scraping_str        = "(Click to STOP) Scraping..."
        self.printCompanies_str         = "Print companies"
        self.printMetrics_str           = "metrics"
        self.printMetricsSimple_str     = "metrics simple"
        self.printCalculations_str      = "calculations"
        self.filter_str                 = "Filter companies"
        self.organize_str               = "Organize companies"
        self.exit_str                   = "Exit"
        self.null_filename              = "Select file"

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
        self.ProgressCheckBox = QCheckBox("Show Progress")
        self.ProgressCheckBox.setCheckState(Qt.Checked)
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
        self.ProgressCheckBox.stateChanged.connect(self.setShowProgress)
        self.FileComboBox.currentTextChanged.connect(self.setFilename)

        # layout boxes
        hbox_Checkboxes = QHBoxLayout()
        hbox_Checkboxes.addWidget(self.DebugCheckBox)
        hbox_Checkboxes.addWidget(self.ProgressCheckBox)
        hbox_Checkboxes.addStretch(1)
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
        vbox_main.addLayout(hbox_Checkboxes)
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
            logger_handler.setFormatter(logging.Formatter("%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s"))
            #logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
            logger.setLevel(logging.DEBUG)
        else:
            logger_handler.setFormatter(logging.Formatter('%(message)s'))
            #logging.basicConfig(format="%(message)s")
            logger.setLevel(logging.INFO)
    
    def setShowProgress(self):
        if self.ProgressCheckBox.isChecked():
            self.showProgress = True
        else:
            self.showProgress = False
        self.setScraping()

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

    def setNewestFileFromToday(self):
        if len(self.FileComboBox) > 1:
            s = "scrape_metrics_" + date.today().strftime(scraping.date_format) # YYYY-MM-DD
            if self.FileComboBox.itemText(1).startswith(s):
                self.FileComboBox.setCurrentIndex(1)

    def setFilename(self):
        if self.FileComboBox.currentText() == self.null_filename:
            self.filename = None
        else:
            self.filename = "{}\\{}".format(self.storage_directory, self.FileComboBox.currentText())

    def buttonClicked(self):
        sender = self.sender()
        if sender.text() == self.scrape_str:
            self.startScraping()
        elif sender.text() == self.during_scraping_str:
            self.scraping_terminated = True
            self.terminate_scraping_sig.emit()
            #self.scrapeThread.terminate()
        elif sender.text() == self.exit_str:
            self.scrapeThread.terminate()
            self.close()
        elif self.filename and not self.scraping:
            print_type = None
            company_id = None
            company_name = None
            if sender.text() == self.filter_str:
                scrapeKL.filter_companies(self.filename)
            elif sender.text() == self.organize_str:
                scrapeKL.organize_companies(self.filename)
            elif sender.text() == self.printCompanies_str:
                scrapeKL.print_companies(self.filename)
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
                scrapeKL.print_company_metrics(self.filename, print_type, company_id, company_name)
        elif self.scraping:
            logger.info("Can not do that while scraping")
        else:
            logger.info("No file selected")


if __name__ == '__main__':
    logger = logging.getLogger('root')
    #logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
    #logging.basicConfig(format="%(message)s")

    logger_handler = logging.StreamHandler()
    logger.addHandler(logger_handler)
    logger_handler.setFormatter(logging.Formatter('%(message)s'))

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
