""" csv-files separated by: ';' """

import os, logging, json
from datetime import datetime

import scraping

logger = logging.getLogger('root')


def store_company_data(company_list, storage_directory, scrape_type):
    # YY-MM-DD_HH-MM-SS
    datetime_str = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
    tsv_filename = storage_directory + "\\scrape_{}_{}.tsv".format(scrape_type, datetime_str)

    with open(tsv_filename, "w") as f:
        f.write("Companies scraped from www.kauppalehti.fi\n" +\
                "scrape_{}\n".format(scrape_type) +\
                "storage_datetime:\t{}\n".format(datetime_str) +\
                "###")
        if scrape_type == "names":
            for i in company_list:
                f.write("\n{}\t{}".format(i, company_list[i]))
        elif scrape_type == "raw":
            for company in company_list:
                f.write(company.tsv_raw)
        elif scrape_type == "metrics":
            for company in company_list:
                f.write(company.tsv_metrics)
        elif scrape_type == "raw_metrics":
            for company in company_list:
                f.write(company.tsv_raw_metrics)
        else:
            logger.error("Not a valid scrape_type: [{}]".format(scrape_type))

    logger.debug("Stored scrape_{} into: {}".format(scrape_type, tsv_filename))
    return tsv_filename

def get_stored_company_data(filename):
    logger.debug("Reading from file: " + filename)
    company_list = []
    company = None          # Company Object
    scrape_type = None      # name, raw, metrics, raw_metrics
    storage_datetime = None # datetime.datetime Object
    sub_header = None       # e.g. Osingot, Perustiedot

    body_lines = False
    line = True
    with open(filename, "r") as f:
        while line:
            line = f.readline().strip()

            if not body_lines:
                # reading the files header
                #print(line.rstrip())
                if line.startswith("scrape"):
                    scrape_type = line.strip().split("scrape_")[1]
                    logger.debug("scrape_type: [{}]".format(scrape_type))
                elif line.startswith("storage_datetime:"):
                    storage_datetime = datetime.strptime(line.strip().split("\t")[1], "%y-%m-%d_%H-%M-%S")
                    logger.debug("storage_datetime: [{}]".format(storage_datetime))
                elif line.startswith("###"):
                    body_lines = True
                    if not scrape_type:
                        logger.error("No scrape_type")
                        return None, None

            elif body_lines and line:
                # reading the files body
                if scrape_type == "raw_metrics":
                    json_acceptable_string = line.replace("'", "\"")
                    #logger.debug("json_acceptable_string: [{}]".format(json_acceptable_string))
                    company_list.append(scraping.Company(raw_metrics = json.loads(json_acceptable_string)))
                else:
                    try:
                        parts = line.strip().split("\t")
                    except ValueError:
                        logger.error("Error in file [{}] with line [{}].".format(filename, line))
                        return None, None
                    print(parts)

                    # process parts
                    if parts[0].startswith("##"):
                        if company:
                            company_list.append(company)
                        if sub_header:
                            sub_header = None
                        company = scraping.Company(int(parts[1]))
                        logger.debug("company: {}".format(str(company)))
                    elif parts[0].startswith("#"):
                        sub_header = parts[0].strip("# ")
                        logger.debug("sub_header: [{}]".format(sub_header))

                    elif not sub_header:
                        pass
                    elif sub_header == "osingot":
                        pass
                    elif sub_header == "perustiedot":
                        pass
                    elif sub_header == "tunnuslukuja":
                        pass
                    elif sub_header == "toiminnan_laajuus":
                        pass
                    elif sub_header == "kannattavuus":
                        pass
                    elif sub_header == "vakavaraisuus":
                        pass
                    elif sub_header == "maksuvalmius":
                        pass
                    elif sub_header == "sijoittajan_tunnuslukuja":
                        pass
                    else:
                        logger.error("Unexpected sub_header: [{}]".format(sub_header))

            elif body_lines and not line:
                # EOF: add the last company to the list
                if company:
                    company_list.append(company)

    return company_list, scrape_type

def get_today_stored_company_names(storage_directory):
    # YY-MM-DD
    date_str = datetime.now().strftime("%y-%m-%d")
    filename_start_today = "scrape_names_{}".format(date_str)

    files = os.listdir(storage_directory)
    for filename in files:
        if filename.startswith(filename_start_today):
            matching_filename = storage_directory +'\\'+ filename
            logger.debug("Using ready company names from file : " + matching_filename)
            company_names = {}
            body_lines = False
            line = True
            with open(matching_filename, "r") as f:
                while line:
                    line = f.readline()
                    if body_lines and line:
                        try:
                            c_id, c_name = line.strip().split("\t")
                            c_id = int(c_id)
                            company_names[c_id] = c_name
                        except ValueError:
                            logger.error("Error in names file [{}] with line [{}]. Will scrape names.".format(matching_filename, line))
                            return None
                    if line.startswith("###"):
                        body_lines = True
            return company_names
    return None
