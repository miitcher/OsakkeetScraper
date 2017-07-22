import logging

import scraping
import storage

logger = logging.getLogger('root')

#import webbrowser # WHAT IS THIS/COULD BE USED FOR ???


def scrape_companies(storage_directory):
    logger.debug("Check if company_names is already fetched today")
    company_names = storage.get_today_stored_company_names(storage_directory)

    if not company_names:
        logger.debug("Company names are scraped from Kauppalehti")
        company_names = scraping.scrape_company_names()
        storage.store_company_data(company_names, storage_directory, "names")

    logger.debug("Individual companies data is scraped from Kauppalehti")
    company_list = []
    for company_id in company_names:
        logger.debug("company_id:{}, Name:{}".format(company_id, company_names[company_id]))
        company = scraping.Company(company_id, name=company_names[company_id])
        company.scrape()
        company_list.append(company)
        break # so just one company is scraped
    logger.debug("Number of companies scraped: {}".format(len(company_list)))

    logger.debug("Scraped companies are stored")
    tsv_filename_raw         = storage.store_company_data(company_list, storage_directory, "raw")
    tsv_filename_metrics     = storage.store_company_data(company_list, storage_directory, "metrics")

    return tsv_filename_metrics

def load_companies(filename):
    # TODO: function can be removed
    # but the used function below can be elsewhere used
    # can use load_companies for testing for now
    company_list = scraping.Company.load_from_file(filename)

def print_companies(filename):
    """
    if self.Tiedot:
        for ID in self.Tiedot.scraped_IDs:
            print("{} {}".format(ID, self.Tiedot.DICT_yritys[ID]))
    else:
        print("TIEDOT is missing")
    """
    pass

def print_company(filename, ID):
    """
    if ID in self.Tiedot.scraped_IDs:
        print("{} {}".format(ID, self.Tiedot.DICT_yritys[ID]))
        matrix_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID][0])
        kurssi_tiedot_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
        kurssi_tulostiedot_print(self.Tiedot.DICT_YRITYKSEN_TIEDOT[ID])
    else:
        print("There is no company scraped with ID: {}".format(ID))
    """
    pass

def filter_companies(filename):
    pass

def organize_companies(filename):
    pass
