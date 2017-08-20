import logging, json, sys, os

import scraping
import storage



logger = logging.getLogger('root')

"""
When a company is scraped, its raw metrics is stored.
When a company is loaded, the calculations are done,
and the company is not stored again.
"""


class ScrapeKLException(Exception):
    pass


def scrape_companies(storage_directory, company_names=None, showProgress=True):
    assert company_names is None or isinstance(company_names, dict)
    logger.info("Scraping starts")
    if company_names is None or len(company_names) == 0:
        company_names = get_company_names(storage_directory)

    metrics_list = scraping.scrape_companies_with_processes(
        company_names, showProgress
    )

    # Find failed scrapes
    failed_company_dict = {}
    for metrics in metrics_list:
        if len(metrics) < 3:
            assert len(metrics) == 2, "metrics entries: {}".format(len(metrics))
            failed_company_dict[metrics["company_id"]] = metrics["company_name"]
            logger.debug("Failed: Company({}, {})".format(
                metrics["company_id"], metrics["company_name"]
            ))

    company_count = len(company_names)
    company_failed_count = len(failed_company_dict)
    assert company_count == len(metrics_list)
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

    metrics_filename = storage.store_metrics(storage_directory, metrics_list)
    logger.info("Companies stored in file: {}".format(metrics_filename))

    return metrics_list, failed_company_dict, metrics_filename

def print_names(storage_directory=None, names_filename=None,
                company_names=None):
    # Only one input is allowed.
    if storage_directory:
        assert names_filename is None and company_names is None
        company_names = get_company_names(storage_directory)
    elif names_filename:
        assert storage_directory is None and company_names is None
        company_names = storage.load_names(names_filename)
    elif company_names:
        assert storage_directory is None and names_filename is None
    else:
        raise ScrapeKLException

    c_strings = []
    for c_id in sorted(company_names, key=company_names.get):
        c_strings.append("({}, {})".format(c_id, company_names[c_id]))

    c_len = max(len(s) for s in c_strings) + 2
    format_str = "{:" + str(c_len) + "." + str(c_len) + "}"

    out_str = ""
    i = 0
    for c_str in c_strings:
        if i%2 == 0 and i != 0:
            out_str += "\n"
        out_str += format_str.format(c_str)
        i += 1
    logger.info("\n" + "-"*10 + "\tNAMES")
    logger.info(out_str)

def print_metrics(metrics_filename, company_id=None, company_name=None):
    # Only one of company_id and company_name is allowed.
    if company_id is not None:
        assert company_name is None, "Too many filters"
    if company_name is not None:
        assert company_id is None, "Too many filters"
    logger.debug("Filters: id={}; name={}".format(company_id, company_name))

    metrics_list = storage.load_metrics(metrics_filename)
    metrics_printed = False
    logger.info("\n" + "-"*10 + "\tMETRICS"
                + "\n\tfile:    {}".format(metrics_filename))
    for metrics in metrics_list:
        if ( company_id and company_id == metrics["company_id"] ) \
        or ( company_name and str(company_name).lower() \
                                in str(metrics["company_name"]).lower() ):
            logger.info("\tcompany: {}, {}".format(
                metrics["company_id"], metrics["company_name"]
            ))
            logger.info(json.dumps(metrics, indent=3))
            metrics_printed = True

    if not metrics_printed:
        logger.info("Nothing found")

def print_calculations(metrics_filename, company_id=None, company_name=None):
    # Only one of company_id and company_name is allowed.
    if company_id is not None:
        assert company_name is None, "Too many filters"
    if company_name is not None:
        assert company_id is None, "Too many filters"
    logger.debug("Filters: id={}; name={}".format(company_id, company_name))

    metrics_list = storage.load_metrics(metrics_filename)
    calculations_printed = False
    logger.info("\n" + "-"*10 + "\tCALCULATIONS"
                + "\n\tfile:    {}".format(metrics_filename))
    for metrics in metrics_list:
        if ( company_id and company_id == metrics["company_id"] ) \
        or ( company_name and str(company_name).lower() \
                                in str(metrics["company_name"]).lower() ):
            logger.info("\tcompany: {}, {}".format(
                metrics["company_id"], metrics["company_name"]
            ))
            company = scraping.Company(c_metrics=metrics)
            logger.info(json.dumps(company.calculations, indent=3))
            calculations_printed = True

    if not calculations_printed:
        logger.info("Nothing found")

def filter_companies(metrics_filename):
    # TODO: Done after metrics is scraped properly.
    logger.info("Not implemented")

def organize_companies(metrics_filename):
    # TODO: Done after metrics is scraped properly.
    logger.info("Not implemented")


def get_company_names(storage_directory):
    company_names = storage.load_todays_names(storage_directory)
    if not company_names:
        logger.debug("Company names are scraped from Kauppalehti")
        company_names = scraping.scrape_company_names()
        storage.store_names(storage_directory, company_names)
    return company_names


console_instructions = \
"ScrapeKL\n\
 s, scrape\n\
 f, files\n\
 n, names [file]\n\
 m, metrics <file> [--name=<name> | --id=<id>]"


logger_format_long = \
    "%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s"
logger_format_short = '%(message)s'


if __name__ == '__main__':
    logger = logging.getLogger('root')
    logger_handler = logging.StreamHandler()
    logger.addHandler(logger_handler)
    logger_handler.setFormatter(logging.Formatter(logger_format_short))
    logger.setLevel(logging.INFO)

    logger_handler.setFormatter(logging.Formatter(logger_format_long))

    storage_directory = "scrapes"

    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print(console_instructions)
    elif sys.argv[1] == "scrape" or sys.argv[1] == "s":
        company_names = scrape_companies(storage_directory)
    elif sys.argv[1] == "files" or sys.argv[1] == "f":
        all_filenames = os.listdir(storage_directory)
        stored_filenames = []
        for f in sorted(all_filenames):
            if f.endswith(".json"):
                print(f)
    elif sys.argv[1] == "names" or sys.argv[1] == "n":
        if len(sys.argv) == 3:
            names_filename = sys.argv[2]
            print_names(names_filename=names_filename)
        else:
            print_names(storage_directory=storage_directory)
    elif sys.argv[1] == "metrics" or sys.argv[1] == "m":
        if not ( len(sys.argv) == 3 or len(sys.argv) == 4 ):
            print(console_instructions)
        elif len(sys.argv) == 3:
            metrics_filename = sys.argv[2]
            print_metrics("scrapes\\" + metrics_filename)
        else:
            metrics_filename = sys.argv[2]
            company_id = None
            company_name = None
            choice = sys.argv[3]
            try:
                company_id = int(choice)
            except ValueError:
                company_name = choice
            print_metrics(
                "scrapes\\" + metrics_filename,
                company_id=company_id, company_name=company_name
            )
    else:
        print(console_instructions)
