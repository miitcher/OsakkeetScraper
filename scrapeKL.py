import logging, json, sys, os

import scraping
import storage



logger = logging.getLogger('root')

"""
When a company is scraped, its raw metrics is stored.
When a company is loaded, the calculations are done,
and the company is not stored again.
"""


def scrape_companies(storage_directory, company_names, showProgress=True):
    assert isinstance(company_names, dict)
    logger.info("Scraping starts")
    if len(company_names) == 0:
        company_names = get_company_names(storage_directory)

    json_metrics_list = scraping.scrape_companies_with_processes(
        company_names, showProgress
    )

    # Find failed scrapes
    failed_company_dict = {}
    for json_metrics in json_metrics_list:
        if len(json_metrics) < 100:
            json_acceptable_string = json_metrics.replace("'", "\"")
            metrics = json.loads(json_acceptable_string)
            failed_company_dict[metrics["company_id"]] = metrics["company_name"]
            logger.debug("Failed: Company({}, {})".format(
                metrics["company_id"], metrics["company_name"]
            ))

    company_count = len(company_names)
    company_failed_count = len(failed_company_dict)
    assert company_count == len(json_metrics_list)
    logger.info("Scraping done:\t{}/{}\tFailed: {}".format(
        company_count - company_failed_count,
        company_count, company_failed_count)
    )

    if company_failed_count > 0:
        failed_companies_str = "\n\tFailed Companies ({}):\n".format(
            len(failed_company_dict)) + "-"*40
        i = 1
        for c_id in sorted(failed_company_dict, key=failed_company_dict.get):
            failed_companies_str += "\n\t{:3}. ({}, {})".format(
                i, c_id, failed_company_dict[c_id]
            )
            i += 1
        failed_companies_str += "\n" + "-"*40
        logger.info(failed_companies_str)

    metricsfilename = storage.store_company_list_json(json_metrics_list,
                                                      storage_directory)

    return json_metrics_list, failed_company_dict, metricsfilename

def print_companies(storage_directory, filename=None, return_output=False):
    if filename is None:
        company_names = get_company_names(storage_directory)
        c_strings = []
        for c_id in sorted(company_names, key=company_names.get):
            c_strings.append("Company({}, {})".format(c_id,
                                                      company_names[c_id]))

        c_len = max(len(s) for s in c_strings) + 1
        format_str = "{:" + str(c_len) + "." + str(c_len) + "}"

        out_str = ""
        i = 0
        for c_str in c_strings:
            if i%2 == 0 and i != 0:
                out_str += "\n"
            out_str += format_str.format(c_str)
            i += 1
        print(out_str)
    else:
        # TODO: Check that this works
        company_list = storage.load_company_list(filename)
        output_str = ""
        for company in company_list:
            output_str += str(company)
        if return_output:
            return output_str
        else:
            print("Print all companies:\n" + output_str)

def print_company_metrics(filename, print_type, company_id=None,
                          company_name=None, return_output=False):
    company_list = storage.load_company_list(filename)
    output_str = ""
    for company in company_list:
        if ( not company_id and not company_name ) \
        or ( company_id and company_id == company.company_id ) \
        or ( company_name and str(company_name).lower() \
                                in str(company.company_name).lower() ):
            if print_type == "metrics":
                output_str += company.str_metrics
            elif print_type == "metrics_simple":
                output_str += company.str_metrics_simple
            elif print_type == "calculations":
                output_str += company.str_calculations
    if len(output_str) == 0:
        if company_id:
            logger.info("Found no company with company_id: [{}]".format(
                company_id
            ))
        if company_name:
            logger.info("Found no company with company_name: [{}]".format(
                company_name
            ))
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


console_instructions = "-"*20 + \
"\n|ScrapeKL Commands:\n\
| scrape\n\
| files\n\
| companies <file>"

if __name__ == '__main__':
    storage_directory = "scrapes"

    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print(console_instructions)
    elif sys.argv[1] == "scrape":
        print("Not implemneted")
    elif sys.argv[1] == "files":
        all_filenames = os.listdir(storage_directory)
        stored_filenames = []
        for f in reversed(all_filenames):
            if f.endswith(".tsv") and f.startswith("scrape_metrics"):
                print(f)
    elif sys.argv[1] == "companies":
        if len(sys.argv) == 3:
            filename = sys.argv[2]
            print("filename: " + filename)
            print("Not implemneted")
        else:
            print_companies(storage_directory)
    else:
        print(console_instructions)
