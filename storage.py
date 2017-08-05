import os, json, logging
from datetime import datetime, date

import scraping

logger = logging.getLogger('root')


def _load_company_names(filename):
    logger.debug("Using company names from file : " + filename)
    company_names = {}
    in_body = False
    line = True
    with open(filename, "r") as f:
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
                    logger.error("Error in names file [{}] with line [{}]. Will scrape names.".format(filename, line))
                    return None
    return company_names

def load_todays_company_names(storage_directory):
    date_str = date.today().strftime(scraping.date_short_format) # YY-MM-DD
    filename_start_today = "scrape_names_{}".format(date_str)
    files = os.listdir(storage_directory)
    for filename_end in files:
        if filename_end.startswith(filename_start_today):
            filename = storage_directory +'\\'+ filename_end
            return _load_company_names(filename)
    return None

def load_company_list(filename):
    logger.debug("Reading file: " + filename)
    company_list = []
    scrape_type = None
    in_body = False
    line = True
    with open(filename, "r") as f:
        while line:
            line = f.readline().strip()
            if not in_body:
                # header
                if line.startswith("scrape"):
                    scrape_type = line.split("scrape_")[1]
                elif line.startswith("###"):
                    in_body = True
                    assert scrape_type == "metrics", "Not a valid scrape_type: [{}]".format(str(scrape_type))
            elif in_body and line:
                # body
                json_acceptable_string = line.replace("'", "\"")
                #logger.debug("json_acceptable_string: [{}]".format(json_acceptable_string))
                company_list.append(scraping.Company(c_metrics=json.loads(json_acceptable_string)))
    logger.debug("Loaded {} companies from {}".format(len(company_list), filename))
    return company_list

def _store_company_data(company_data, storage_directory, scrape_type, filename=None):
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
            assert isinstance(company.tsv_metrics, str)
    else:
        raise AssertionError("Invalid scrape_type")

    datetime_str = datetime.now().strftime(scraping.datetime_format)
    if not filename:
        filename = storage_directory + "\\scrape_{}_{}.tsv".format(scrape_type, datetime_str)
    with open(filename, "w") as f:
        f.write("Companies scraped from www.kauppalehti.fi\n" +\
                "scrape_{}\n".format(scrape_type) +\
                "storage_datetime:\t{}\n".format(datetime_str) +\
                "###")
        if scrape_type == "names":
            for company_id in sorted(company_data, key=company_data.get):
                f.write("\n{}\t{}".format(company_id, company_data[company_id]))
        elif scrape_type == "metrics":
            for company in sorted(company_data, key=lambda Company: Company.company_name):
                f.write(company.tsv_metrics)
        else:
            logger.error("Not a valid scrape_type: [{}]".format(scrape_type))
    logger.debug("Stored scrape_{} into: {}".format(scrape_type, filename))
    return filename

def store_company_names(company_names, storage_directory, filename=None):
    return _store_company_data(company_names, storage_directory, "names", filename)

def store_company_list(company_list, storage_directory, filename=None):
    return _store_company_data(company_list, storage_directory, "metrics", filename)
