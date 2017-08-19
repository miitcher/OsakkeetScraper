import os, json, logging
from datetime import datetime, date

import scraping

logger = logging.getLogger('root')


class StorageException(Exception):
    pass


def store_names(storage_directory, company_names, names_filename=None):
    assert isinstance(company_names, dict)
    for company_id in company_names:
        assert isinstance(company_id, int)
        assert isinstance(company_names[company_id], str)

    datetime_str = datetime.now().strftime(scraping.datetime_format)
    if not names_filename:
        names_filename = storage_directory + "\\names_{}.tsv".format(
            datetime_str
        )

    with open(names_filename, "w") as f:
        f.write("source: www.kauppalehti.fi\n" +\
                "stored:\t{}\n###".format(datetime_str))
        for company_id in sorted(company_names, key=company_names.get):
            f.write("\n{}\t{}".format(company_id, company_names[company_id]))

    logger.debug("Stored names into: {}".format(names_filename))
    return names_filename

def load_names(names_filename):
    logger.debug("Loading names from file : {}".format(names_filename))
    company_names = {}
    in_body = False
    line = True
    with open(names_filename, "r") as f:
        while line:
            line = f.readline().strip()
            if not in_body:
                # header
                if line.startswith("###"):
                    in_body = True
            elif in_body and line:
                # body
                try:
                    c_id, c_name = line.split("\t")
                    c_id = int(c_id)
                    company_names[c_id] = c_name
                except ValueError:
                    logger.error("Invalid line [{}] in names file [{}]".format(
                        line, names_filename
                    ))
                    return None
    return company_names

def load_todays_names(storage_directory):
    date_str = date.today().strftime(scraping.date_short_format) # YY-MM-DD
    filename_start_today = "names_{}".format(date_str)
    files = os.listdir(storage_directory)
    for filename_end in files:
        if filename_end.startswith(filename_start_today):
            filename = storage_directory +'\\'+ filename_end
            company_names = load_names(filename)
            if len(company_names) < 100:
                raise StorageException("Too few companies: {}".format(len(company_names)))
            return company_names
    return None

def store_metrics(storage_directory, metrics_list, metrics_filename=None):
    assert isinstance(metrics_list, list)
    for metrics in metrics_list:
        assert isinstance(metrics, dict), metrics

    datetime_str = datetime.now().strftime(scraping.datetime_format)
    if not metrics_filename:
        metrics_filename = storage_directory + "\\metrics_{}.json".format(
            datetime_str
        )

    with open(metrics_filename, "w") as json_file:
        json.dump({"metrics": metrics_list}, json_file, indent=3)

    logger.debug("Stored metrics into: {}".format(metrics_filename))
    return metrics_filename

def load_metrics(metrics_filename):
    logger.debug("Loading metrics from file : {}".format(metrics_filename))
    with open(metrics_filename, "r") as json_file:
        metrics_dict = json.load(json_file)
    metrics_list = metrics_dict["metrics"]
    return metrics_list
