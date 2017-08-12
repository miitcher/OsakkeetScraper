import traceback, logging, json

import scraping
import storage



logger = logging.getLogger('root')

"""
When a company is scraped, its raw metrics is stored.
When a company is loaded, the calculations are done,
and the company is not stored again.
"""


def scrape_companies(storage_directory, company_names, showProgress=True, terminate_scraping_sig=None):
    # No return values so function can be used as threads target.
    # Explains also the strict input values
    assert isinstance(storage_directory, str)
    assert isinstance(company_names, dict)
    logger.info("Scraping starts")
    if len(company_names) == 0:
        company_names = get_company_names(storage_directory)

    if terminate_scraping_sig is None:
        json_metrics_list = scraping.scrape_companies_with_processes(company_names, showProgress)
    else:
        companyScraper = scraping.QCompanyScraper(terminate_scraping_sig, company_names, showProgress)
        companyScraper.startScraping()
        json_metrics_list = companyScraper.json_metrics_list

    # Find failed scrapes
    failed_company_dict = {}
    for json_metrics in json_metrics_list:
        if len(json_metrics) < 100:
            json_acceptable_string = json_metrics.replace("'", "\"")
            #logger.debug("json_acceptable_string: {}".format(json_acceptable_string))
            metrics = json.loads(json_acceptable_string)
            failed_company_dict[metrics["company_id"]] = metrics["company_name"]
            #logger.debug("Failed: Company({}, {})".format(metrics["company_id"], metrics["company_name"]))

    company_count = len(company_names)
    company_failed_count = len(failed_company_dict)
    assert company_count == len(json_metrics_list)
    logger.info("Scraping done:\t{}/{}\tFailed: {}".format(
        company_count - company_failed_count,
        company_count, company_failed_count)
    )

    if company_failed_count > 0:
        failed_companies_str = "\n\tFailed Companies ({}):\n".format(len(failed_company_dict)) + "-"*40
        c = 1
        for company_id in sorted(failed_company_dict, key=failed_company_dict.get):
            failed_companies_str += "\n\t{:3}. ({}, {})".format(c, company_id, failed_company_dict[company_id])
            c += 1
        failed_companies_str += "\n" + "-"*40
        logger.info(failed_companies_str)

    metricsfilename = storage.store_company_list_json(json_metrics_list, storage_directory)

    return json_metrics_list, failed_company_dict, metricsfilename

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
