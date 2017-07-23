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
        logger.debug("company_id:{}, company_name:{}".format(company_id, company_names[company_id]))
        company = scraping.Company(company_id, name=company_names[company_id])
        company.scrape()
        company_list.append(company)
        break # TODO: so just one company is scraped
    logger.debug("Number of companies scraped: {}".format(len(company_list)))

    tsv_filename_metrics = storage.store_company_data(company_list, storage_directory, "metrics")
    return tsv_filename_metrics

def print_companies(filename):
    logger.info("Print all companies:")
    company_list = scraping.Company.load_from_file(filename)
    for company in company_list:
        print(company)

def print_company_metrics(filename, simple, company_id=None, company_name=None):
    company_list = scraping.Company.load_from_file(filename)
    if not company_id and not company_name:
        logger.info("Print all companies info:")
    company_printed = False
    for company in company_list:
        if ( not company_id and not company_name ) or \
           ( company_id and company_id == company.company_id ) or \
           ( company_name and str(company_name).lower() in str(company.company_name).lower() ):
            if simple:
                print(company.str_metrics_simple)
            else:
                print(company.str_metrics)
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
