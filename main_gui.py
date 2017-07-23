import os, sys, logging, traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from datetime import datetime

import scrape_KL


class Window(QWidget):
    def __init__(self, storage_dir):
        super().__init__()
        self.storage_dir = storage_dir
        self.tsv_filename = None
        self.setWindowTitle('OsakkeetScraper Kauppalehdesta')
        self.setWindow()
        self.setLoggingLevel()
        self.refreshFileComboBox()
        self.setNewestTsvFileFromToday()

    def setWindow(self):
        # strings
        self.scrape_str                 = "Scrape companies"
        self.printCompanies_str         = "Print companies"
        self.printMetrics_str           = "metrics"
        self.printMetricsSimple_str     = "metrics simple"
        self.printCalculations_str      = "calculations"
        self.filter_str                 = "Filter companies"
        self.organize_str               = "Organize companies"
        self.null_filename              = "Select TSV-file"

        # buttons
        ScrapeButton                = QPushButton(self.scrape_str)
        PrintCompaniesButton        = QPushButton(self.printCompanies_str)
        PrintMetricsButton          = QPushButton(self.printMetrics_str)
        PrintMetricsSimpleButton    = QPushButton(self.printMetricsSimple_str)
        PrintCalculationsButton     = QPushButton(self.printCalculations_str)
        FilterButton                = QPushButton(self.filter_str)
        OrganizeButton              = QPushButton(self.organize_str)
        ExitButton                  = QPushButton("Exit")

        # other widgets
        self.DebugCheckBox = QCheckBox("DEBUG")
        self.DebugCheckBox.setCheckState(Qt.Checked)
        self.CompanySearchLineEdit = QLineEdit(self)
        self.FileComboBox = QComboBox()
        self.FileComboBox.setMaxVisibleItems(30)

        # connect buttons and widgets
        ScrapeButton.clicked.connect(self.scrapebuttonClicked)
        PrintCompaniesButton.clicked.connect(self.buttonClicked)
        PrintMetricsButton.clicked.connect(self.buttonClicked)
        PrintMetricsSimpleButton.clicked.connect(self.buttonClicked)
        PrintCalculationsButton.clicked.connect(self.buttonClicked)
        FilterButton.clicked.connect(self.buttonClicked)
        OrganizeButton.clicked.connect(self.buttonClicked)
        ExitButton.clicked.connect(self.close)
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
        vbox_main.addWidget(ScrapeButton)
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
        all_filenames = os.listdir(self.storage_dir)
        stored_filenames = []
        for f in reversed(all_filenames):
            if f.endswith(".tsv") and f.startswith("scrape_metrics"):
                stored_filenames.append(f)
        self.FileComboBox.addItems(stored_filenames)

    def setNewestTsvFileFromToday(self):
        if len(self.FileComboBox) > 1:
            s = "scrape_metrics_" + datetime.now().strftime("%y-%m-%d")
            if self.FileComboBox.itemText(1).startswith(s):
                self.FileComboBox.setCurrentIndex(1)

    def setTsvFilename(self):
        if self.FileComboBox.currentText() == self.null_filename:
            self.tsv_filename = None
        else:
            self.tsv_filename = "{}\\{}".format(self.storage_dir, self.FileComboBox.currentText())

    def scrapebuttonClicked(self):
        try:
            tsv_filename_metrics = scrape_KL.scrape_companies(self.storage_dir)
            if tsv_filename_metrics:
                logger.info("Scraping done")
                self.refreshFileComboBox()
                self.FileComboBox.setCurrentIndex(1)
            else:
                logger.error("Scraping failed")
        except:
            # The traceback does not work properly with the PyQt in LiClipse.
            # There is no traceback on errors in LiClipse, but there is
            # when running the program from the command line.
            traceback.print_exc()

    def buttonClicked(self):
        sender = self.sender()
        if self.tsv_filename:
            print_type = None
            company_id = None
            company_name = None
            try:
                if sender.text() == self.filter_str:
                    scrape_KL.filter_companies(self.tsv_filename)
                elif sender.text() == self.organize_str:
                    scrape_KL.organize_companies(self.tsv_filename)
                elif sender.text() == self.printCompanies_str:
                    scrape_KL.print_companies(self.tsv_filename)
                elif sender.text() == self.printMetrics_str:
                    print_type = "metrics"
                elif sender.text() == self.printMetricsSimple_str:
                    print_type = "metrics_simple"
                elif sender.text() == self.printCalculations_str:
                    print_type = "calculations"
                else:
                    logger.error('Did not recognize "sender.text()": [{}]'.format(sender.text()))
                if print_type != None:
                    search_line_str = self.CompanySearchLineEdit.text().strip()
                    if search_line_str != "":
                        try:
                            company_id = int(search_line_str)
                        except ValueError:
                            company_name = search_line_str
                    scrape_KL.print_company_metrics(self.tsv_filename, print_type, company_id, company_name)
            except:
                # The traceback does not work properly with the PyQt in LiClipse.
                # There is no traceback on errors in LiClipse, but there is
                # when running the program from the command line.
                traceback.print_exc()
        else:
            logger.info("No TSV-file selected")


if __name__ == '__main__':
    logger = logging.getLogger('root')
    logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
    logger.setLevel(logging.DEBUG)
    #logger.setLevel(logging.INFO)

    storage_dir = "scrapes"
    #Creates a storage-folder if one does not exist.
    if not os.path.isdir(storage_dir):
        os.makedirs(storage_dir)
        logger.debug("storage-folder created: [{}]".format(storage_dir))

    app = QApplication(sys.argv)
    Window = Window(storage_dir)
    Window.show()
    sys.exit(app.exec_())
