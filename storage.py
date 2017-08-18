import os, json, logging
from datetime import datetime, date

import scraping

logger = logging.getLogger('root')


class StorageException(Exception):
    pass


def load_company_names(names_filename):
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

def load_todays_company_names(storage_directory):
    date_str = date.today().strftime(scraping.date_short_format) # YY-MM-DD
    filename_start_today = "names_{}".format(date_str)
    files = os.listdir(storage_directory)
    for filename_end in files:
        if filename_end.startswith(filename_start_today):
            filename = storage_directory +'\\'+ filename_end
            company_names = load_company_names(filename)
            if len(company_names) < 100:
                raise StorageException("Too few companies: {}".format(len(company_names)))
            return company_names
    return None

def load_metrics(metrics_filename):
    logger.debug("Loading names from file : {}".format(metrics_filename))
    metrics_list = []
    in_body = False
    line = True
    with open(metrics_filename, "r") as f:
        while line:
            line = f.readline().strip()
            if not in_body:
                # header
                if line.startswith("###"):
                    in_body = True
            elif in_body and line:
                # body
                try:
                    json_acceptable_string = line.replace("'", "\"")
                    metrics = json.loads(json_acceptable_string)
                    metrics_list.append(metrics)
                except:
                    logger.error("Invalid line in metrics file [{}]".format(
                        metrics_filename
                    ))
                    return None
    return metrics_list

def _store_company_data(company_data, storage_directory,
                        scrape_type, filename=None):
    # store company names or metrics to file
    # the data is stored in alphabetical order by the company_name
    if scrape_type == "names":
        assert isinstance(company_data, dict)
        for company_id in company_data:
            assert isinstance(company_id, int)
            assert isinstance(company_data[company_id], str)
    elif scrape_type == "metrics":
        assert isinstance(company_data, list)
        for company in company_data:
            assert isinstance(company, scraping.Company)
            assert isinstance(company.json_metrics, str)
    elif scrape_type == "metrics_json":
        assert isinstance(company_data, list)
        for json_metrics in company_data:
            assert isinstance(json_metrics, str)
            assert len(json_metrics) > 35
    else:
        raise AssertionError("Invalid scrape_type")

    datetime_str = datetime.now().strftime(scraping.datetime_format)
    if not filename:
        filename = storage_directory + "\\{}_{}.tsv".format(scrape_type,
                                                            datetime_str)
    with open(filename, "w") as f:
        f.write("Companies scraped from www.kauppalehti.fi\n" +\
                "{}\n".format(scrape_type) +\
                "storage_datetime:\t{}\n".format(datetime_str) +\
                "###")
        if scrape_type == "names":
            for company_id in sorted(company_data, key=company_data.get):
                f.write("\n{}\t{}".format(company_id, company_data[company_id]))
        elif scrape_type == "metrics":
            for company in sorted(company_data,
                                  key=lambda Company: Company.company_name):
                f.write(company.json_metrics)
        elif scrape_type == "metrics_json":
            for json_metrics in sorted(company_data):
                f.write(json_metrics)
        else:
            logger.error("Not a valid scrape_type: [{}]".format(scrape_type))
    logger.debug("Stored {} into: {}".format(scrape_type, filename))
    return filename

def store_company_names(company_names, storage_directory, filename=None):
    return _store_company_data(company_names, storage_directory,
                               "names", filename)

def store_company_list(company_list, storage_directory, filename=None):
    return _store_company_data(company_list, storage_directory,
                               "metrics", filename)

def store_company_list_json(json_metrics_list, storage_directory,
                            filename=None):
    return _store_company_data(json_metrics_list, storage_directory,
                               "metrics_json", filename)
