"""
Usage:
  scrapeKL.py scrape [--id=<int>...] [options]
  scrapeKL.py names [<file>] [options]
  scrapeKL.py metrics (--name=<str> | --id=<int>...) [<file>] [options]
  scrapeKL.py collection (--name=<str> | --id=<int>...) [<file>] [options]
  scrapeKL.py filtered [--name=<str> | --id=<int>...] [<file>] [options]
  scrapeKL.py passed [<file>] [options]
  scrapeKL.py list_files [options]
  scrapeKL.py speed [<times>] [options]

Options:
  -h, --help
  --debug
"""
from docopt import docopt
import logging, json, os, time

import scraping
import processing
import storage
import scrape_logger
import speed

logger = logging.getLogger('root')


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

def _get_metrics_list(filename, c_id_list, c_name):
    # Only one or none of c_id and c_name is allowed.
    if c_id_list:
        assert isinstance(c_id_list, list)
        assert c_name is None, "Too many filters"
    if c_name:
        assert isinstance(c_name, str)
        assert not c_id_list, "Too many filters"
    logger.debug("Filters: c_id_list={}; c_name={}".format(c_id_list, c_name))

    metrics_list = storage.load_metrics(filename)
    if not c_id_list and not c_name:
        return metrics_list
    else:
        retval = []
        for metrics in metrics_list:
            if ( c_id_list and metrics["company_id"] in c_id_list) \
            or ( c_name and str(c_name).lower() \
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

def _print_master(header, filename, c_id_list, c_name, print_func):
    metrics_list = _get_metrics_list(filename, c_id_list, c_name)
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

def print_metrics(filename, c_id_list, c_name):
    _print_master("METRICS", filename, c_id_list, c_name,
                  _print_metrics)

def _print_collection(metrics):
    processor = processing.Processor(metrics)
    collection = processor.process()
    logger.info(json.dumps(collection, indent=3))

def print_collection(filename, c_id_list, c_name):
    _print_master("COLLECTION", filename, c_id_list, c_name,
                  _print_collection)

def _print_filtered(metrics):
    processor = processing.Processor(metrics)
    collection = processor.process()
    logger.info(json.dumps(collection["passed_filter"], indent=3))

def print_filtered(filename, c_id_list, c_name):
    _print_master("FILTERED", filename, c_id_list, c_name,
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


def main(arguments):
    # Logging
    if arguments["--debug"]:
        level = "DEBUG"
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
    c_name = arguments["--name"]
    c_id_list_in = arguments["--id"]
    c_id_list = []
    if c_id_list_in:
        for c_id in c_id_list_in:
            try:
                c_id_list.append(int(c_id))
            except ValueError:
                raise ScrapeKLException(
                    "Id {} is not an integer.".format(c_id))
    logger.debug("c_id_list: {}; c_name: {}".format(c_id_list, c_name))

    # Function calling
    if arguments["scrape"]:
        company_names = None
        if arguments["--id"]:
            company_names = {}
            for c_id in arguments["--id"]:
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
        print_metrics(filename, c_id_list, c_name)

    elif arguments["collection"]:
        print_collection(filename, c_id_list, c_name)

    elif arguments["filtered"]:
        print_filtered(filename, c_id_list, c_name)

    elif arguments["passed"]:
        print_passed_names(filename)

    elif arguments["list_files"]:
        all_filenames = os.listdir(storage_directory)
        for f in sorted(all_filenames):
            if f.endswith(".json"):
                print(f)

    elif arguments["speed"]:
        times = arguments["<times>"]
        if times:
            try:
                times = int(times)
            except ValueError:
                raise ScrapeKLException(
                    "Times {} is not an integer.".format(times))
            assert times > 0
        else:
            logger.info("Using default: times = 5")
            times = 5

        """
        The speed testing needs its own logger, so the print is clean.
        The speed logger level is gotten from the user input,
        and the scrape logger, "root", level is set to WARNING.
        """
        _speed_logger = scrape_logger.setup_logger(logger.level, "speed")
        scrape_logger.set_logger_level(logger, "WARNING")

        speed.run_speedtest(times)

if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
