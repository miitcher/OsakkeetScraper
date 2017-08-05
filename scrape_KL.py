import traceback, logging

import scraping
import storage

from PyQt5.Qt import QThread, pyqtSignal
import time

logger = logging.getLogger('root')

"""
When a company is scraped, its raw metrics is stored.
When a company is loaded, the calculations are done,
and the company is not stored again.
"""


class scrapeCompanyThread(QThread):
    # Create signal
    add_company_sig = pyqtSignal(scraping.Company)

    def __init__(self, c_id, c_name):
        QThread.__init__(self)
        assert isinstance(c_id, int)
        assert isinstance(c_name, str)
        self.c_id = c_id
        self.c_name = c_name

    def __del__(self):
        self.wait()

    def run(self):
        logger.debug("Starting scrapeCompanyThread: c_id:{}, c_name:{}".format(self.c_id, self.c_name))
        company = scraping.Company(c_id=self.c_id, c_name=self.c_name)
        try:
            company.scrape()
        except:
            company.scraping_failed = True
            pass #traceback.print_exc()
        self.add_company_sig.emit(company)
        #print(company)


class scrapeThread(QThread):
    # Create signals
    company_names_len_sig = pyqtSignal(int)
    company_processed_sig = pyqtSignal()

    def __init__(self, terminate_all_scrapeThreads_sig, storage_directory, company_names=None):
        QThread.__init__(self)
        terminate_all_scrapeThreads_sig.connect(self.terminate_scrapeThreads)
        self.storage_directory = storage_directory
        if company_names:
            self.company_names = company_names
        else:
            self.company_names = get_company_names(storage_directory)
        self.threads = None

    def __del__(self):
        self.wait()

    def terminate_scrapeThreads(self):
        try:
            logger.info("Stop scraping")
            print("self.running_treads_id: " + str(self.running_treads_id))
            print("self.threads")
            for i in sorted(self.threads):
                print(i)
            for company_id in self.running_treads_id:
                print("terminate: " + str(company_id))
                self.threads[company_id].terminate()
            print("after loop")
            self.terminate()
        except:
            traceback.print_exc()

    def create_scrapeCompanyThreads(self):
        self.threads = {}
        for company_id in self.company_names:
            scrapeC_thread = scrapeCompanyThread(company_id, self.company_names[company_id])
            scrapeC_thread.add_company_sig.connect(self.add_scraped_company)
            #scrapeC_thread.finished.connect(self.scrapingCompanyDone)
            self.threads[company_id] = scrapeC_thread
        logger.debug("All threads created")

    def add_scraped_company(self, company):
        print("IN add_scraped_company WITH " + str(company))
        try:
            self.company_processed_sig.emit()
            self.active_thread_count -= 1

            if not company.scraping_failed:
                print("FAIL" + str(company))
                self.company_list.append(company)
            print("1" + str(company))
            self.threads.pop(company.company_id)
            print("2" + str(company))
            self.running_treads_id.remove(company.company_id)
            print("3" + str(company))
            for company_id in self.threads:
                self.running_treads_id.append(company_id)
                self.threads[company_id].start()
                break
        except:
            traceback.print_exc()
        print("OUT add_scraped_company WITH " + str(company))
    """
    def scrapingCompanyDone(self):
        self.company_processed_sig.emit()
        self.active_thread_count -= 1
    """
    def run(self):
        logger.debug("Individual companies data is scraped from Kauppalehti")
        self.company_list = []
        self.active_thread_count = len(self.company_names)
        self.given_companies_count = self.active_thread_count
        self.company_names_len_sig.emit(self.active_thread_count)
        logger.debug("scrapeCompanyThreads: {}".format(self.active_thread_count))

        self.create_scrapeCompanyThreads()
        self.running_treads_id = []
        self.running_threads_max = 7
        c = 0
        for company_id in self.threads:
            self.running_treads_id.append(company_id)
            self.threads[company_id].start()
            c += 1
            if c == self.running_threads_max:
                break

        while self.active_thread_count > 0:
            pass #time.sleep(1)

        logger.info("{} companies scraped, out of {} given".format(len(self.company_list), self.given_companies_count))
        #_filename_metrics = storage.store_company_list(self.company_list, self.storage_directory)
        logger.info("Scraping done")


def scrape_companies(storage_directory, company_names=None):
    # OLD WAY TO SCRAPE
    try:
        if not company_names:
            company_names = get_company_names(storage_directory)
        logger.debug("Individual companies data is scraped from Kauppalehti")
        company_list = []
        for company_id in company_names:
            logger.debug("Scrape: company_id:{}, company_name:{}".format(company_id, company_names[company_id]))
            company = scraping.Company(c_id=company_id, c_name=company_names[company_id])
            company.scrape()
            company_list.append(company)
        if len(company_list) == 0:
            raise scraping.ScrapeException("Scraping failed")
        logger.debug("Number of companies scraped: {}".format(len(company_list)))
        _filename_metrics = storage.store_company_list(company_list, storage_directory)
        logger.info("Scraping done")
    except:
        traceback.print_exc()

def print_companies(filename, return_output=False):
    company_list = storage.load_company_list(filename)
    output_str = ""
    for company in company_list:
        output_str += str(company)
    if return_output:
        return output_str
    else:
        print("Print all companies:\n" + output_str)

def print_company_metrics(filename, print_type, company_id=None, company_name=None, return_output=False):
    company_list = storage.load_company_list(filename)
    output_str = ""
    for company in company_list:
        if ( not company_id and not company_name ) or \
           ( company_id and company_id == company.company_id ) or \
           ( company_name and str(company_name).lower() in str(company.company_name).lower() ):
            if print_type == "metrics":
                output_str += company.str_metrics
            elif print_type == "metrics_simple":
                output_str += company.str_metrics_simple
            elif print_type == "calculations":
                output_str += company.str_calculations
    if len(output_str) == 0:
        if company_id:
            logger.info("Found no company with company_id: [{}]".format(company_id))
        if company_name:
            logger.info("Found no company with company_name: [{}]".format(company_name))
    elif return_output:
        return output_str
    else:
        if not company_id and not company_name:
            print("Print all companies metrics:")
        else:
            print("Print company metrics:")
        print(output_str)

def filter_companies(filename):
    # TODO: Done after metrics is scraped properly.
    pass

def organize_companies(filename):
    # TODO: Done after metrics is scraped properly.
    pass


def get_company_names(storage_directory):
    company_names = storage.load_todays_company_names(storage_directory)
    if not company_names:
        logger.debug("Company names are scraped from Kauppalehti")
        company_names = scraping.scrape_company_names()
        storage.store_company_names(company_names, storage_directory)
    return company_names
