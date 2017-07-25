import os, json, logging
from datetime import datetime, date

import scraping

logger = logging.getLogger('root')


def load_company_list(filename):
    company_list = get_stored_companies(filename)
    logger.debug("Loaded {} companies from {}".format(len(company_list), filename))
    return company_list

def store_company_list(company_list, storage_directory):
    return store_company_data(company_list, storage_directory, "metrics")


def store_company_data(company_list, storage_directory, scrape_type):
    # stores names or metrics
    datetime_str = datetime.now().strftime(scraping.datetime_format)
    tsv_filename = storage_directory + "\\scrape_{}_{}.tsv".format(scrape_type, datetime_str)

    with open(tsv_filename, "w") as f:
        f.write("Companies scraped from www.kauppalehti.fi\n" +\
                "scrape_{}\n".format(scrape_type) +\
                "storage_datetime:\t{}\n".format(datetime_str) +\
                "###")
        if scrape_type == "names":
            for i in company_list:
                f.write("\n{}\t{}".format(i, company_list[i]))
        elif scrape_type == "metrics":
            for company in company_list:
                f.write(company.tsv_metrics)
        else:
            logger.error("Not a valid scrape_type: [{}]".format(scrape_type))

    logger.debug("Stored scrape_{} into: {}".format(scrape_type, tsv_filename))
    return tsv_filename

def get_stored_companies(filename):
    logger.debug("Reading from file: " + filename)
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
    return company_list

def get_today_stored_company_names(storage_directory):
    # YY-MM-DD
    date_str = date.today().strftime(scraping.date_format)
    filename_start_today = "scrape_names_{}".format(date_str)

    files = os.listdir(storage_directory)
    for filename in files:
        if filename.startswith(filename_start_today):
            matching_filename = storage_directory +'\\'+ filename
            logger.debug("Using ready company names from file : " + matching_filename)
            company_names = {}
            in_body = False
            line = True
            with open(matching_filename, "r") as f:
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
                            logger.error("Error in names file [{}] with line [{}]. Will scrape names.".format(matching_filename, line))
                            return None
            return company_names
    return None
