import os, sys, logging, traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

import scrape_KL


class Window(QWidget):
    def __init__(self, storage_dir):
        super().__init__()
        self.storage_dir = storage_dir
        self.tsv_filename = None
        self.setWindowTitle('Osakkeiden loytaminen Kauppalehdesta')
        self.setWindow()
        self.set_logging_level()
        self.RefreshFileComboBox()

    def setWindow(self):
        # strings
        self.scrape_str         = "Scrape companies"
        self.load_str           = "Load"
        self.printCompanies_str = "Print companies"
        self.printInfo_str      = "Print company info"
        self.filter_str         = "Filter companies"
        self.organize_str       = "Organize companies"
        self.null_filename      = "Select TSV-file"

        # buttons
        ScrapeButton         = QPushButton(self.scrape_str)
        LoadButton           = QPushButton(self.load_str)
        PrintCompaniesButton = QPushButton(self.printCompanies_str)
        PrintInfoButton      = QPushButton(self.printInfo_str)
        FilterButton         = QPushButton(self.filter_str)
        OrganizeButton       = QPushButton(self.organize_str)
        ExitButton           = QPushButton("Exit")

        # other widgets
        self.debugCheckBox = QCheckBox("DEBUG")
        self.debugCheckBox.setCheckState(Qt.Checked)
        self.company_ID = QLineEdit(self)
        self.FileComboBox = QComboBox()
        # TODO: minimum ComboBox width
        self.FileComboBox.setMaxVisibleItems(30)
        self.showMetricsCheckBox = QCheckBox("metrics")
        self.showMetricsCheckBox.setCheckState(Qt.Checked)
        self.showRawCheckBox = QCheckBox("raw")

        # connect buttons and widgets
        ScrapeButton.clicked.connect(self.ScrapeButtonClicked)
        LoadButton.clicked.connect(self.ButtonClicked)
        PrintCompaniesButton.clicked.connect(self.ButtonClicked)
        PrintInfoButton.clicked.connect(self.ButtonClicked)
        FilterButton.clicked.connect(self.ButtonClicked)
        OrganizeButton.clicked.connect(self.ButtonClicked)
        ExitButton.clicked.connect(self.close)
        self.debugCheckBox.stateChanged.connect(self.set_logging_level)
        self.FileComboBox.currentTextChanged.connect(self.set_tsv_filename)
        self.showMetricsCheckBox.stateChanged.connect(self.RefreshFileComboBox)
        self.showRawCheckBox.stateChanged.connect(self.RefreshFileComboBox)

        # layout boxes
        hbox_PrintInfo = QHBoxLayout()
        hbox_PrintInfo.addWidget(QLabel("ID"))
        hbox_PrintInfo.addWidget(self.company_ID)
        hbox_PrintInfo.addWidget(PrintInfoButton)
        vbox_CheckBoxes = QVBoxLayout()
        vbox_CheckBoxes.addWidget(self.showMetricsCheckBox)
        vbox_CheckBoxes.addWidget(self.showRawCheckBox)
        hbox_StoredFiles = QHBoxLayout()
        hbox_StoredFiles.addWidget(self.FileComboBox)
        hbox_StoredFiles.addLayout(vbox_CheckBoxes)
        hbox_StoredFiles.addWidget(LoadButton)

        # layout
        space = 15
        vbox_main = QVBoxLayout()
        vbox_main.addWidget(self.debugCheckBox)
        vbox_main.addWidget(ScrapeButton)
        vbox_main.addLayout(hbox_StoredFiles)
        vbox_main.addSpacing(space)
        vbox_main.addWidget(PrintCompaniesButton)
        vbox_main.addLayout(hbox_PrintInfo)
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

    def set_logging_level(self):
        if self.debugCheckBox.isChecked():
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def RefreshFileComboBox(self):
        i = self.FileComboBox.count()
        while i > 0:
            self.FileComboBox.removeItem(0)
            i -= 1
        self.FileComboBox.addItem(self.null_filename)
        all_filenames = os.listdir(self.storage_dir)
        stored_filenames = []
        for f in reversed(all_filenames):
            if f.endswith(".tsv") and ( \
              ( f.startswith("scrape_metrics") and self.showMetricsCheckBox.isChecked() ) or \
              ( f.startswith("scrape_raw") and self.showRawCheckBox.isChecked() ) ):
                stored_filenames.append(f)
        self.FileComboBox.addItems(stored_filenames)

    def set_tsv_filename(self):
        if self.FileComboBox.currentText() == self.null_filename:
            self.tsv_filename = None
        else:
            self.tsv_filename = "{}\\{}".format(self.storage_dir, self.FileComboBox.currentText())

    def ScrapeButtonClicked(self):
        try:
            tsv_filename_metrics = scrape_KL.scrape_companies(self.storage_dir)
            if tsv_filename_metrics:
                logger.info("Scraping done")
                self.showMetricsCheckBox.setCheckState(Qt.Checked)
                self.showRawCheckBox.setCheckState(Qt.Unchecked)
                self.RefreshFileComboBox()
                self.FileComboBox.setCurrentIndex(1)
            else:
                logger.error("Scraping failed")
            logger.debug("tsv_filename: [{}]".format(str(self.tsv_filename)))
        except:
            # The traceback does not work properly with the PyQt in LiClipse.
            # There is no traceback on errors in LiClipse, but there is
            # when running the program from the command line.
            traceback.print_exc()

    def ButtonClicked(self):
        sender = self.sender()
        if self.tsv_filename:
            try:
                if sender.text() == self.load_str:
                    scrape_KL.load_companies(self.tsv_filename)
                    # TODO: as in print below
                    print("REMOVE LOAD BUTTON: loading is called when self.tsv_filename is used")
                elif sender.text() == self.filter_str:
                    scrape_KL.filter_companies(self.tsv_filename)
                elif sender.text() == self.organize_str:
                    scrape_KL.organize_companies(self.tsv_filename)
                elif sender.text() == self.printCompanies_str:
                    scrape_KL.print_companies(self.tsv_filename)
                elif sender.text() == self.printInfo_str:
                    try:
                        company_ID = int(self.company_ID.text())
                        scrape_KL.print_company(self.tsv_filename, company_ID)
                    except ValueError:
                        logger.info("The company-ID must be an integer.")
                else:
                    logger.error('Did not recognize "sender.text()": ' + sender.text())
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
