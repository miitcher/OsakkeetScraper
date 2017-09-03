"""
Usage:
  scrapeKL.py scrape [--ids=<int>...] [options]
  scrapeKL.py names [<file>] [options]
  scrapeKL.py metrics [<file>] [--name=<str> | --id=<int>] [options]
  scrapeKL.py collection [<file>] [--name=<str> | --id=<int>] [options]
  scrapeKL.py filtered [<file>] [--name=<str> | --id=<int>] [options]
  scrapeKL.py passed [<file>] [options]
  scrapeKL.py list_files [options]

Options:
  -h, --help
  --debug
  -q, --quiet
"""
from docopt import docopt
import logging, json, os, time

import scraping
import processing
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

def _print_names(company_names):
    assert isinstance(company_names, dict)
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
    logger.info(out_str)

def print_all_names(storage_directory=None, names_filename=None):
    if storage_directory:
        assert names_filename is None
        company_names = get_company_names(storage_directory)
    elif names_filename:
        assert storage_directory is None
        company_names = storage.load_names(names_filename)
    logger.info("-"*14 + "\tALL NAMES")
    _print_names(company_names)

def _get_metrics_list(filename, company_id, company_name):
    # Only one or none of company_id and company_name is allowed.
    if company_id is not None:
        assert company_name is None, "Too many filters"
    if company_name is not None:
        assert company_id is None, "Too many filters"
    logger.debug("Filters: id={}; name={}".format(company_id, company_name))

    metrics_list = storage.load_metrics(filename)
    if company_id is None and company_name is None:
        return metrics_list
    else:
        retval = []
        for metrics in metrics_list:
            if ( company_id and company_id == metrics["company_id"] ) \
            or ( company_name and str(company_name).lower() \
                                    in str(metrics["company_name"]).lower() ):
                retval.append(metrics)
        return retval

def print_passed_names(filename):
    metrics_list = _get_metrics_list(filename, None, None)
    company_names = {}
    for metrics in metrics_list:
        processor = processing.Processor(metrics)
        collection = processor.process()
        if collection != "FAIL":
            #logger.info(json.dumps(collection["passed_filter"], indent=3))
            if collection["passed_filter"]["all"]:
                company_names[collection["company_id"]] = \
                    collection["company_name"]
        else:
            logger.debug("Failed collection: c_id: {}, c_name:{}".format(
                metrics["company_id"], metrics["company_name"]))
    logger.info("-"*14 + "\tPASSED NAMES")
    _print_names(company_names)

def _print_master(header, filename, company_id, company_name, print_func):
    assert company_id or company_name, "Need some limiter."
    metrics_list = _get_metrics_list(filename, company_id, company_name)
    if metrics_list:
        logger.info("\t" + header + "\t{}".format(filename))
        for metrics in metrics_list:
            logger.info("-"*14)
            logger.info("\tcompany: {}, {}".format(
                metrics["company_id"], metrics["company_name"]
            ))

            print_func(metrics)

            logger.info("-"*14)
        logger.info("\t" + header + "\t{}".format(filename))
    else:
        logger.info("Nothing found")

def _print_metrics(metrics):
    logger.info(json.dumps(metrics, indent=3))

def print_metrics(filename, company_id, company_name):
    _print_master("METRICS", filename, company_id, company_name,
                  _print_metrics)

def _print_collection(metrics):
    processor = processing.Processor(metrics)
    collection = processor.process()
    logger.info(json.dumps(collection, indent=3))

def print_collection(filename, company_id, company_name):
    _print_master("COLLECTION", filename, company_id, company_name,
                  _print_collection)

def _print_filtered(metrics):
    processor = processing.Processor(metrics)
    collection = processor.process()
    logger.info(json.dumps(collection["passed_filter"], indent=3))

def print_filtered(filename, company_id, company_name):
    _print_master("FILTERED", filename, company_id, company_name,
                  _print_filtered)

def organize_companies(filename):
    # TODO: Done after metrics is scraped properly.
    logger.info("Not implemented")


def get_company_names(storage_directory):
    company_names = storage.load_todays_names(storage_directory)
    if not company_names:
        logger.debug("Company names are scraped from Kauppalehti")
        company_names = scraping.scrape_company_names()
        storage.store_names(storage_directory, company_names)
    return company_names

def _get_commandline_filters(choice):
    company_id = None
    company_name = None
    try:
        company_id = int(choice)
    except ValueError:
        company_name = choice
    return company_id, company_name

console_instructions = \
"ScrapeKL  If no metrics file is specified, the latest is used.\n\
 SCRAPE                s [<id>]\n\
 LIST FILES            files\n\
 LIST NAMES            n [<file>]\n\
 SHOW METRICS          m [<file>] [<name> | <id>]\n\
 SHOW COLLECTION       c [<file>] [<name> | <id>]\n\
 SHOW FILTERED         f [<file>] [<name> | <id>]\n\
 LIST PASSED FILTER    p [<file>]"

def main(arguments):
    # Logging
    if arguments["--debug"] and arguments["--quiet"]:
        raise ScrapeKLException("Can not have debug and quiet.")
    if arguments["--debug"]:
        level = "DEBUG"
    elif arguments["--quiet"]:
        level = "WARNING"
    else:
        level = "INFO"
    logger = scrape_logger.setup_logger(level)

    logger.debug(arguments)

    # Storage
    storage_directory = "scrapes"
    if not os.path.isdir(storage_directory):
        os.makedirs(storage_directory)
        logger.debug("storage-folder created: [{}]".format(storage_directory))


    # Shared arguments
    if arguments["<file>"]:
        filename = storage_directory +"\\" + arguments["<file>"]
    else:
        filename = storage.get_latest_metrics_filename(storage_directory)
    company_name = arguments["--name"]
    company_id = arguments["--id"]
    if company_id:
        try:
            company_id = int(company_id)
        except ValueError:
            raise ScrapeKLException(
                "Id {} is not an integer.".format(company_id))
    logger.debug("ID: {}; NAME: {}".format(company_id, company_name))

    # Function calling
    if arguments["scrape"]:
        company_names = None
        if arguments["--ids"]:
            company_names = {}
            for c_id in arguments["--ids"]:
                try:
                    company_names[int(c_id)] = None
                except ValueError:
                    raise ScrapeKLException(
                        "Id {} is not an integer.".format(c_id))
        logger.debug("company_names to scrape: {}".format(company_names))
        time0 = time.time()
        scrape_companies(storage_directory, company_names)
        print("Scraping took: {:.2f} s".format(time.time() - time0))

    elif arguments["names"]:
        if arguments["<file>"]:
            names_filename = arguments["<file>"]
            print_all_names(names_filename=names_filename)
        else:
            print_all_names(storage_directory=storage_directory)

    elif arguments["metrics"]:
        print_metrics(filename, company_id, company_name)

    elif arguments["collection"]:
        print_collection(filename, company_id, company_name)

    elif arguments["filtered"]:
        print_filtered(filename, company_id, company_name)

    elif arguments["passed"]:
        print_passed_names(filename)

    elif arguments["list_files"]:
        all_filenames = os.listdir(storage_directory)
        for f in sorted(all_filenames):
            if f.endswith(".json"):
                print(f)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
