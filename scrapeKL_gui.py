import os, sys, logging, time, traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, \
    QPushButton, QCheckBox, QComboBox, QLineEdit, QLabel
from PyQt5.Qt import QThread
from datetime import date
from multiprocessing import Queue

from scraping import date_format
import scrapeKL
import scrape_logger


logger = logging.getLogger('root')


class ScrapeGuiException(Exception):
    pass


class scrapeThread(QThread):

    def __init__(self, storage_directory, company_names,
                 showProgress, queue):
        QThread.__init__(self)
        self.storage_directory = storage_directory
        self.company_names = company_names
        self.showProgress = showProgress
        self.queue = queue

    def run(self):
        logger.debug("Starting scraping from QThread")
        if not self.showProgress:
            logger.debug("Hide progress")
        try:
            time0 = time.time()
            metrics_list, failed_company_dict, metricsfilename \
                = scrapeKL.scrape_companies(
                    self.storage_directory, self.company_names,
                    self.showProgress
                )
            logger.debug("Scraping took: {:.2f} s".format(time.time() - time0))
            self.queue.put(
                (metrics_list, failed_company_dict, metricsfilename)
            )
        except:
            traceback.print_exc()


class Window(QWidget):

    def __init__(self, storage_directory):
        super().__init__()
        self.storage_directory = storage_directory
        self.filename = None

        self.setWindow()
        self.setLoggingLevel()
        self.setShowProgress()
        self.refreshFileComboBox()
        self.setNewestFileFromToday()
        self.setScraping()

    def setScraping(self):
        self.metrics_list = None
        self.failed_company_dict = None
        self.metricsfilename = None

        self.currently_scraping = False
        self.scrape_queue = Queue()
        company_names = None
        #company_names = {2048:"talenom", 1906:"cargotec", 1196:"afarak group"}
        self.scrapeThread = scrapeThread(self.storage_directory, company_names,
                                         self.showProgress, self.scrape_queue)
        self.scrapeThread.finished.connect(self.scrapingDone)

    def startScraping(self):
        self.currently_scraping = True

        self.ScrapeButton.setText(self.during_scraping_str)
        self.ScrapeButton.setEnabled(False)
        self.DebugCheckBox.setEnabled(False)
        self.ProgressCheckBox.setEnabled(False)
        self.FileComboBox.setEnabled(False)

        self.scrapeThread.start()

    def scrapingDone(self):
        # TODO: The metrics are not used at the moment...
        self.metrics_list, self.failed_company_dict, \
            self.metricsfilename = self.scrape_queue.get()

        self.refreshFileComboBox()
        self.FileComboBox.setCurrentIndex(1)

        self.ScrapeButton.setText(self.scrape_str)
        self.ScrapeButton.setEnabled(True)
        self.DebugCheckBox.setEnabled(True)
        self.ProgressCheckBox.setEnabled(True)
        self.FileComboBox.setEnabled(True)

        self.currently_scraping = False

    def setWindow(self):
        self.setWindowTitle('OsakkeetScraper Kauppalehdesta')

        # strings
        self.scrape_str                 = "Scrape companies"
        self.during_scraping_str        = "Scraping..."
        self.printCompanies_str         = "Print companies"
        self.printMetrics_str           = "metrics"
        self.printCalculations_str      = "calculations"
        self.filter_str                 = "Filter companies"
        self.organize_str               = "Organize companies"
        self.exit_str                   = "Exit"
        self.null_filename              = "Select file"

        # buttons
        self.ScrapeButton           = QPushButton(self.scrape_str)
        PrintCompaniesButton        = QPushButton(self.printCompanies_str)
        PrintMetricsButton          = QPushButton(self.printMetrics_str)
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
            scrape_logger.set_logger_level(logger, "DEBUG")
        else:
            scrape_logger.set_logger_level(logger, "INFO")

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
            if f.endswith(".json"):
                stored_filenames.append(f)
        self.FileComboBox.addItems(stored_filenames)

    def setNewestFileFromToday(self):
        if len(self.FileComboBox) > 1:
            # YYYY-MM-DD
            s = "metrics_" + date.today().strftime(date_format)
            if self.FileComboBox.itemText(1).startswith(s):
                self.FileComboBox.setCurrentIndex(1)

    def setFilename(self):
        if self.FileComboBox.currentText() == self.null_filename:
            self.filename = None
        else:
            self.filename = "{}\\{}".format(self.storage_directory,
                                            self.FileComboBox.currentText())

    def getSearchFilters(self):
        company_id = None
        company_name = None
        search_line_str = self.CompanySearchLineEdit.text().strip()
        if search_line_str != "":
            try:
                company_id = int(search_line_str)
            except ValueError:
                company_name = search_line_str
        return company_id, company_name

    def buttonClicked(self):
        sender = self.sender()
        if self.currently_scraping:
            logger.info("Can not do that while scraping")
        else:
            if sender.text() == self.scrape_str:
                self.startScraping()
            elif sender.text() == self.printCompanies_str:
                scrapeKL.print_names(self.storage_directory)
            elif sender.text() == self.exit_str:
                self.close()

            elif self.filename:
                if sender.text() == self.printMetrics_str:
                    c_id, c_name = self.getSearchFilters()
                    scrapeKL.print_metrics(self.filename, c_id, c_name)
                elif sender.text() == self.printCalculations_str:
                    c_id, c_name = self.getSearchFilters()
                    scrapeKL.print_calculations(self.filename, c_id, c_name)

                # TODO: Filter and organize functions does not work atm
                elif sender.text() == self.filter_str:
                    scrapeKL.filter_companies(self.filename)
                elif sender.text() == self.organize_str:
                    scrapeKL.organize_companies(self.filename)

                else:
                    raise ScrapeGuiException(
                        'Unexpected "sender.text()": [{}]'.format(sender.text())
                    )
            else:
                logger.info("No file selected")


if __name__ == '__main__':
    logger = scrape_logger.setup_logger("DEBUG")

    # Storage
    storage_directory = "scrapes"
    if not os.path.isdir(storage_directory):
        os.makedirs(storage_directory)
        logger.debug("storage-folder created: [{}]".format(storage_directory))

    # GUI
    app = QApplication(sys.argv)
    Window = Window(storage_directory)
    Window.show()
    sys.exit(app.exec_())
