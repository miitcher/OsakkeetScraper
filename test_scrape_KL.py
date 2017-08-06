import os, unittest, logging
import time

import scrape_KL
from PyQt5.Qt import QWidget, QThread

show_debug = False
show_debug = True

logger = logging.getLogger('root')
logging.basicConfig(format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s")
if not show_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)


url_basic = "http://www.kauppalehti.fi/5/i/porssi/"
osingot_url             = url_basic + "osingot/osinkohistoria.jsp"
osingot_yritys_url      = url_basic + "osingot/osinkohistoria.jsp?klid={}"
kurssi_url              = url_basic + "porssikurssit/osake/index.jsp?klid={}"
kurssi_tulostiedot_url  = url_basic + "porssikurssit/osake/tulostiedot.jsp?klid={}"

storage_directory = "scrapes"

some_company_ids = [2048, 1032, 1135, 1120, 1105]


class Test(unittest.TestCase):
    """
    def test_scrape_companies_One_OLD(self):
        filename = scrape_KL.scrape_companies(storage_directory, {2048:"talenom"})
        self.assertTrue(os.path.isfile(filename))

        output_str = scrape_KL.print_companies(filename, return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrape_KL.print_company_metrics(filename, "metrics", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrape_KL.print_company_metrics(filename, "metrics_simple", return_output=True)
        self.assertGreater(len(output_str), 0)
        output_str = scrape_KL.print_company_metrics(filename, "calculations", return_output=True)
        self.assertGreater(len(output_str), 0)
        # TODO: Better validation of print output.

        os.remove(filename)
    """

    """
    def test_scrapeCompanyThread(self):
        company_names = {
            2048: "talenom"
        }

        test_SCThreads_class = test_scrapeCompanyThreads_class(self, company_names)
        #test_SCThreads_class.create_scrapeCompanyThreads()
        #test_SCThreads_class.start_scrapeCompanyThreads()
        test_SCThreads_class.start()

        print("END")
    """
    def test_scrapeThread(self):
        #company_names = {2048:"talenom", 1906:"cargotec", 1196:"afarak group"}
        company_names = {
            2048: "talenom"
        }

        test_SThread_class = test_scrapeThread_class(storage_directory, company_names)

        print("END2")


class test_scrapeCompanyThreads_class(QThread):
    def __init__(self, tester, company_names):
        QThread.__init__(self)
        self.tester = tester
        self.company_names = company_names

    def create_scrapeCompanyThreads(self):
        self.threads = {}
        for company_id in self.company_names:
            SCThread = scrape_KL.scrapeCompanyThread(company_id, self.company_names[company_id])
            SCThread.add_company_sig.connect(self.add_scraped_company)
            self.threads[company_id] = SCThread
        print("All scrapeCompanyThreads created")

    def start_scrapeCompanyThreads(self):
        for SCThread in self.threads.values():
            print(SCThread)
            SCThread.start()

    def add_scraped_company(self, company):
        print("hello")
        print("add_scraped_company " + str(company))
        # TODO: do asserting here

    def __del__(self):
        self.wait()

    def run(self):
        self.create_scrapeCompanyThreads()
        self.start_scrapeCompanyThreads()
        #time.sleep(10)
        c = 0
        while len(self.threads) > 0:
            c += 1
            if c > 100:
                break
        print("class done")


class test_scrapeThread_class():
    def __init__(self, storage_directory, company_names):
        self.scrapeThread = scrape_KL.scrapeThread(storage_directory, company_names)
        self.scrapeThread.finished.connect(self.scrapingDone)
        self.scrapeThread.start()

    def scrapingDone(self):
        whole_scrape_time = time.time() - self.scraping_started_time
        final_average_scrape_time = whole_scrape_time / self.companies_scraped
        time_taken_to_scrape_first_company = self.first_company_scraped_time - self.scraping_started_time
        print("whole_scrape_time: {} s".format(whole_scrape_time))
        print("final_average_scrape_time: {} s".format(final_average_scrape_time))
        print("time_taken_to_scrape_first_company: {} s".format(time_taken_to_scrape_first_company))

        self.ScrapeButton.setText(self.scrape_str)
        if not self.stopThreads:
            self.refreshFileComboBox()
            self.FileComboBox.setCurrentIndex(1)
        else:
            self.stopThreads = False
            self.ScrapingProgressBar.setValue(0)


if __name__ == '__main__':
    unittest.main()
