import traceback, logging

import scraping
import storage



logger = logging.getLogger('root')

"""
When a company is scraped, its raw metrics is stored.
When a company is loaded, the calculations are done,
and the company is not stored again.
"""


def scrape_companies_sequentially(storage_directory, company_names=None):
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


def scrape_companies_with_threads(storage_directory, filename_metrics,
                                  company_names, company_list, company_failed_count):
    # No return values so function can be used as threads target.
    # Explains also the strict input values
    assert isinstance(storage_directory, str)
    assert isinstance(company_names, dict)
    assert company_list == []
    assert company_failed_count == 0
    assert filename_metrics == ""
    logger.debug("Scraping starts")
    if len(company_names) == 0:
        company_names = get_company_names(storage_directory)
    scraping.scrape_companies_with_threads(company_names, company_list, company_failed_count)
    logger.info("Scraping done:\t{}/{}\tFailed: {}".format(
        len(company_list) + company_failed_count,
        len(company_names), company_failed_count)
    )
    filename_metrics += storage.store_company_list(company_list, storage_directory)


def scrape_companies_with_processes(storage_directory, filename_metrics,
                                    company_names, company_list, company_failed_count):
    # No return values so function can be used as threads target.
    # Explains also the strict input values
    assert isinstance(storage_directory, str)
    assert isinstance(company_names, dict)
    assert company_list == []
    assert company_failed_count == 0
    assert filename_metrics == ""
    logger.debug("Scraping starts")
    if len(company_names) == 0:
        company_names = get_company_names(storage_directory)
    scraping.scrape_companies_with_processes(company_names, company_list, company_failed_count)
    logger.info("Scraping done:\t{}/{}\tFailed: {}".format(
        len(company_list) + company_failed_count,
        len(company_names), company_failed_count)
    )
    filename_metrics += storage.store_company_list(company_list, storage_directory)



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
