import logging

import scraping
import storage

logger = logging.getLogger('root')

"""
When a company is scraped, its raw metrics is stored.
When a company is loaded, the calculations are done,
and the company is not stored again.
"""


def scrape_companies(storage_directory, company_names=None):
    if not company_names:
        company_names = get_company_names(storage_directory)
    logger.debug("Individual companies data is scraped from Kauppalehti")
    company_list = []
    for company_id in company_names:
        logger.debug("Scrape: company_id:{}, company_name:{}".format(company_id, company_names[company_id]))
        company = scraping.Company(company_id, company_names[company_id])
        company.scrape()
        company_list.append(company)
        break # TODO: so just one company is scraped
    if len(company_list) == 0:
        raise scraping.ScrapeException("Scraping failed")
    logger.debug("Number of companies scraped: {}".format(len(company_list)))
    tsv_filename_metrics = storage.store_company_list(company_list, storage_directory)
    logger.info("Scraping done")
    return tsv_filename_metrics

def print_companies(filename):
    print("Print all companies:")
    company_list = storage.load_company_list(filename)
    for company in company_list:
        print(company)

def print_company_metrics(filename, print_type, company_id=None, company_name=None):
    company_list = storage.load_company_list(filename)
    if not company_id and not company_name:
        print("Print all companies metrics:")
    company_printed = False
    for company in company_list:
        if ( not company_id and not company_name ) or \
           ( company_id and company_id == company.company_id ) or \
           ( company_name and str(company_name).lower() in str(company.company_name).lower() ):
            if print_type == "metrics":
                print(company.str_metrics)
            elif print_type == "metrics_simple":
                print(company.str_metrics_simple)
            elif print_type == "calculations":
                print(company.str_calculations)
            company_printed = True
    if not company_printed:
        if company_id:
            logger.info("Found no company with company_id: [{}]".format(company_id))
        if company_name:
            logger.info("Found no company with company_name: [{}]".format(company_name))

def filter_companies(filename):
    # TODO:
    pass

def organize_companies(filename):
    # TODO:
    pass


def get_company_names(storage_directory):
    company_names = storage.get_today_stored_company_names(storage_directory)
    if not company_names:
        logger.debug("Company names are scraped from Kauppalehti")
        company_names = scraping.scrape_company_names()
        storage.store_company_data(company_names, storage_directory, "names")
    return company_names
