import logging, json, sys, os, time

import scraping
#import processing
import storage
import scrape_logger

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

    # Find failed and missing scrapes
    failed_dict = {}
    missing_dict = {}
    exp_missing_dict = {}
    for metrics in metrics_list:
        if metrics["failed_metrics"]:
            failed_dict[metrics["company_id"]] = (metrics["company_name"],
                                            metrics["failed_metrics"])
        if metrics["missing_metrics"]:
            missing_dict[metrics["company_id"]] = (metrics["company_name"],
                                            metrics["missing_metrics"])
        if metrics["exp_missing_metrics"]:
            exp_missing_dict[metrics["company_id"]] = (metrics["company_name"],
                                            metrics["exp_missing_metrics"])

    company_count = len(company_names)
    company_failed_count = len(failed_dict)
    assert company_count == len(metrics_list)

    metrics_failed_count = 0
    for t in failed_dict.values():
        metrics_failed_count += len(t[1])
    metrics_missing_count = 0
    for t in missing_dict.values():
        metrics_missing_count += len(t[1])
    exp_metrics_missing_count = 0
    for t in exp_missing_dict.values():
        exp_metrics_missing_count += len(t[1])

    logger.info(
        "Scraping done:\t{}/{}\tFailed Metrics: {}\tMissing Metrics: {}" \
        .format(company_count - company_failed_count, company_count,
                metrics_failed_count, metrics_missing_count)
    )

    if metrics_failed_count > 0:
        logger.info(_log_scrape_dict(failed_dict, "Failed"))
    if metrics_missing_count > 0:
        logger.info(_log_scrape_dict(missing_dict, "(Unexpected) Missing"))
    if exp_metrics_missing_count > 0:
        logger.debug(_log_scrape_dict(exp_missing_dict, "EXPECTED Missing"))

    if company_failed_count > 0 or metrics_missing_count > 0:
        logger.info(
            "Scraping done:\t{}/{}\tFailed Metrics: {}\tMissing Metrics: {}" \
            .format(company_count - company_failed_count, company_count,
                    metrics_failed_count, metrics_missing_count)
        )

    metrics_filename = storage.store_metrics(storage_directory, metrics_list)
    logger.info("Companies stored in file: {}".format(metrics_filename))

    return metrics_list, failed_dict, metrics_filename

def _log_scrape_dict(some_dict, header):
    retval_str = "\n\t" + header + " Metrics ({}):\n".format(len(some_dict))
    retval_str += "-"*80
    i = 1
    for c_id in sorted(some_dict, key=some_dict.get):
        c_name = some_dict[c_id][0]
        failed_on = some_dict[c_id][1]
        retval_str += "\n {:3}. ({}, {})".format(i, c_id, c_name)
        for fail in failed_on:
            retval_str += "\n\t" + fail
        i += 1
    retval_str += "\n" + "-"*80
    return retval_str

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
            """
            company = processing.Company(c_metrics=metrics)
            logger.info(json.dumps(company.calculations, indent=3))
            """
            # TODO: implement
            logger.error("NOT IMPLEMENTED YET")
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
 s, scrape [<id>]\n\
 f, files\n\
 n, names [file]\n\
 m, metrics <file> [<name> | <id>]"


if __name__ == '__main__':
    level = "INFO"
    #level = "DEBUG"
    logger = scrape_logger.setup_logger(level)

    # Storage
    storage_directory = "scrapes"
    if not os.path.isdir(storage_directory):
        os.makedirs(storage_directory)
        logger.debug("storage-folder created: [{}]".format(storage_directory))

    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print(console_instructions)
    elif sys.argv[1] == "scrape" or sys.argv[1] == "s":
        company_names = None
        if len(sys.argv) > 2:
            try:
                company_names = {int(sys.argv[2]): None}
            except ValueError:
                logger.info("Invalid id type: ".format(type(sys.argv[2])))
        logger.debug("company_names to scrape: {}".format(company_names))
        time0 = time.time()
        scrape_companies(storage_directory, company_names)
        print("Scraping took: {:.2f} s".format(time.time() - time0))
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
